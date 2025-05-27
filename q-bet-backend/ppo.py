import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from torch.distributions import Categorical
from action_space import ACTION_SPACE_SIZE
from torch.optim.lr_scheduler import StepLR


class ActorNetwork(nn.Module):
    """Policy network that outputs action probabilities"""

    def __init__(self, input_size, hidden_size=128):
        super(ActorNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, ACTION_SPACE_SIZE)
        
        # Initialize weights with smaller values
        for layer in [self.fc1, self.fc2, self.fc3]:
            nn.init.orthogonal_(layer.weight, gain=0.5)
            nn.init.constant_(layer.bias, 0.0)

    def forward(self, x):
        # Add small epsilon to prevent exact zeros
        x = x + 1e-8
        
        # Apply layer norm to input
        x = (x - x.mean()) / (x.std() + 1e-8)
        
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # Use log_softmax instead of softmax for better numerical stability
        x = F.log_softmax(self.fc3(x), dim=-1)
        # Convert back to probabilities
        x = torch.exp(x)
        # Ensure the sum is 1 and no probability is exactly 0
        x = x + 1e-8
        x = x / x.sum(dim=-1, keepdim=True)
        return x


class CriticNetwork(nn.Module):
    """Value network that estimates state values"""

    def __init__(self, input_size, hidden_size=128):
        super(CriticNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class PPOMemory:
    """Memory buffer for storing trajectories"""

    def __init__(self, batch_size):
        self.states = []
        self.actions = []
        self.probs = []
        self.vals = []
        self.rewards = []
        self.dones = []
        self.batch_size = batch_size

    def generate_batches(self):
        n_states = len(self.states)
        batch_start = np.arange(0, n_states, self.batch_size)
        indices = np.arange(n_states, dtype=np.int64)
        np.random.shuffle(indices)
        batches = [indices[i : i + self.batch_size] for i in batch_start]
        return batches

    def store_memory(self, state, action, probs, vals, reward, done):
        self.states.append(state)
        self.actions.append(action)
        self.probs.append(probs)
        self.vals.append(vals)
        self.rewards.append(reward)
        self.dones.append(done)

    def clear_memory(self):
        self.states = []
        self.actions = []
        self.probs = []
        self.vals = []
        self.rewards = []
        self.dones = []


class PPOAgent:
    """PPO Agent implementation"""

    def __init__(
        self,
        input_size,
        gamma=0.99,
        alpha=0.0003,
        gae_lambda=0.95,
        policy_clip=0.2,
        batch_size=64,
        n_epochs=10,
        lr_step_size=1000,
        lr_gamma=0.9,
        entropy_coef=0.01,  # Entropy coefficient
        max_grad_norm=0.5,  # Maximum gradient norm
    ):
        self.gamma = gamma
        self.policy_clip = policy_clip
        self.n_epochs = n_epochs
        self.gae_lambda = gae_lambda
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm

        self.actor = ActorNetwork(input_size)
        self.critic = CriticNetwork(input_size)
        self.memory = PPOMemory(batch_size)

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=alpha)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=alpha)
        
        self.actor_scheduler = StepLR(self.actor_optimizer, step_size=lr_step_size, gamma=lr_gamma)
        self.critic_scheduler = StepLR(self.critic_optimizer, step_size=lr_step_size, gamma=lr_gamma)

        self.critic_loss = nn.MSELoss()
        self.training_steps = 0

    def choose_action(self, state):
        """Returns an integer action index suitable for list indexing"""
        if not isinstance(state, torch.Tensor):
            state = torch.as_tensor(state, dtype=torch.float32)

        if len(state.shape) == 1:
            state = state.unsqueeze(0)  # Add batch dimension

        with torch.no_grad():
            probs = self.actor(state)
            # Add small epsilon to prevent zero probabilities
            probs = probs + 1e-10
            # Renormalize
            probs = probs / probs.sum(dim=-1, keepdim=True)
            
            dist = Categorical(probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            value = self.critic(state)

        return int(action.item()), log_prob, value

    def learn(self):
        """Update policy and value networks"""
        if len(self.memory.states) == 0:
            return

        for _ in range(self.n_epochs):
            batches = self.memory.generate_batches()

            for batch in batches:
                states = torch.tensor(
                    np.array([self.memory.states[i] for i in batch]),
                    dtype=torch.float32,
                ).to(next(self.actor.parameters()).device)
                
                old_probs = torch.tensor(
                    [self.memory.probs[i] for i in batch],
                    dtype=torch.float32,
                ).to(next(self.actor.parameters()).device)
                
                actions = torch.tensor(
                    [self.memory.actions[i] for i in batch],
                    dtype=torch.long,
                ).to(next(self.actor.parameters()).device)
                
                old_vals = torch.tensor(
                    [self.memory.vals[i] for i in batch],
                    dtype=torch.float32,
                ).to(next(self.actor.parameters()).device)

                # Calculate advantages with clipping
                rewards = []
                discounted_reward = 0
                for reward, done in zip(
                    reversed(self.memory.rewards), reversed(self.memory.dones)
                ):
                    if done:
                        discounted_reward = 0
                    discounted_reward = reward + (self.gamma * discounted_reward)
                    rewards.insert(0, discounted_reward)

                rewards = torch.tensor(rewards, dtype=torch.float32).to(next(self.actor.parameters()).device)
                if len(batch) > 1:  # Only normalize if we have more than one sample
                    rewards = rewards[batch]
                    rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-8)
                else:
                    rewards = rewards[batch]

                advantages = rewards - old_vals.squeeze()
                if len(batch) > 1:  # Only normalize if we have more than one sample
                    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

                # Calculate new probabilities and values with gradient clipping
                new_probs = self.actor(states)
                
                # Ensure valid probability distribution
                new_probs = torch.clamp(new_probs, 1e-7, 1.0)
                new_probs = new_probs / new_probs.sum(dim=-1, keepdim=True)
                
                try:
                    dist = Categorical(new_probs)
                    new_log_probs = dist.log_prob(actions)
                except Exception as e:
                    print(f"Error in probability distribution:")
                    print(f"new_probs shape: {new_probs.shape}")
                    print(f"new_probs sum: {new_probs.sum(dim=-1)}")
                    print(f"new_probs: {new_probs}")
                    raise e

                # Calculate ratio (pi_theta / pi_theta_old) with clipping
                prob_ratio = (new_log_probs - old_probs).exp()
                prob_ratio = torch.clamp(prob_ratio, 0.01, 10.0)

                # Calculate surrogate losses with clipping
                weighted_probs = advantages * prob_ratio
                weighted_clipped_probs = (
                    torch.clamp(prob_ratio, 1 - self.policy_clip, 1 + self.policy_clip)
                    * advantages
                )

                actor_loss = -torch.min(weighted_probs, weighted_clipped_probs).mean()

                # Calculate critic loss with clipping
                critic_values = self.critic(states).squeeze()
                if rewards.shape != critic_values.shape:
                    rewards = rewards.view_as(critic_values)
                critic_loss = self.critic_loss(critic_values, rewards)
                critic_loss = torch.clamp(critic_loss, -10.0, 10.0)

                # Total loss
                total_loss = actor_loss + 0.5 * critic_loss

                # Take gradient steps with clipping
                self.actor_optimizer.zero_grad()
                self.critic_optimizer.zero_grad()
                
                # Check for NaN in loss
                if torch.isnan(total_loss):
                    print("NaN detected in total_loss!")
                    print(f"actor_loss: {actor_loss}")
                    print(f"critic_loss: {critic_loss}")
                    continue
                    
                total_loss.backward()
                
                # Clip gradients
                torch.nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
                torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
                
                # Check for NaN in gradients
                for param in self.actor.parameters():
                    if param.grad is not None:
                        param.grad.data.clamp_(-1, 1)
                for param in self.critic.parameters():
                    if param.grad is not None:
                        param.grad.data.clamp_(-1, 1)
                
                self.actor_optimizer.step()
                self.critic_optimizer.step()

        self.memory.clear_memory()

    def save_models(self, path):
        """Save actor and critic networks"""
        torch.save(self.actor.state_dict(), f"{path}/actor.pth")
        torch.save(self.critic.state_dict(), f"{path}/critic.pth")

    def load_models(self, path):
        """Load actor and critic networks"""
        self.actor.load_state_dict(torch.load(f"{path}/actor.pth"))
        self.critic.load_state_dict(torch.load(f"{path}/critic.pth"))
