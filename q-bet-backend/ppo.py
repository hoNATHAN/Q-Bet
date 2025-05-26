import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from torch.distributions import Categorical
from action_space import ACTION_SPACE_SIZE


class ActorNetwork(nn.Module):
    """Policy network that outputs action probabilities"""

    def __init__(self, input_size, hidden_size=128):
        super(ActorNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, ACTION_SPACE_SIZE)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.softmax(self.fc3(x), dim=-1)
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
    ):
        self.gamma = gamma
        self.policy_clip = policy_clip
        self.n_epochs = n_epochs
        self.gae_lambda = gae_lambda

        self.actor = ActorNetwork(input_size)
        self.critic = CriticNetwork(input_size)
        self.memory = PPOMemory(batch_size)

        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=alpha)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=alpha)

        self.critic_loss = nn.MSELoss()

    def choose_action(self, state):
        """Returns an integer action index suitable for list indexing"""
        if not isinstance(state, torch.Tensor):
            state = torch.as_tensor(state, dtype=torch.float32)

        if len(state.shape) == 1:
            state = state.unsqueeze(0)  # Add batch dimension

        with torch.no_grad():
            probs = self.actor(state)
            dist = Categorical(probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            value = self.critic(state)

        # Ensure action is a Python integer for list indexing
        return int(action.item()), log_prob, value

    def learn(self):
        """Update policy and value networks"""
        for _ in range(self.n_epochs):
            batches = self.memory.generate_batches()

            for batch in batches:
                states = torch.tensor(
                    np.array([self.memory.states[i] for i in batch]),
                    dtype=torch.float32,
                )
                old_probs = torch.tensor(
                    [self.memory.probs[i] for i in batch], dtype=torch.float32
                )
                actions = torch.tensor(
                    [self.memory.actions[i] for i in batch], dtype=torch.float32
                )
                old_vals = torch.tensor(
                    [self.memory.vals[i] for i in batch], dtype=torch.float32
                )

                # Calculate advantages
                rewards = []
                discounted_reward = 0
                for reward, done in zip(
                    reversed(self.memory.rewards), reversed(self.memory.dones)
                ):
                    if done:
                        discounted_reward = 0
                    discounted_reward = reward + (self.gamma * discounted_reward)
                    rewards.insert(0, discounted_reward)

                rewards = torch.tensor(rewards, dtype=torch.float32)[batch]
                advantages = rewards - old_vals.squeeze()

                # Calculate new probabilities and values
                new_probs = self.actor(states)
                dist = Categorical(new_probs)
                new_log_probs = dist.log_prob(actions)

                # Calculate ratio (pi_theta / pi_theta_old)
                prob_ratio = (new_log_probs - old_probs).exp()

                # Calculate surrogate losses
                weighted_probs = advantages * prob_ratio
                weighted_clipped_probs = (
                    torch.clamp(prob_ratio, 1 - self.policy_clip, 1 + self.policy_clip)
                    * advantages
                )

                actor_loss = -torch.min(weighted_probs, weighted_clipped_probs).mean()

                # Calculate critic loss
                critic_values = self.critic(states).squeeze()
                critic_loss = self.critic_loss(critic_values, rewards)

                # Total loss
                total_loss = actor_loss + 0.5 * critic_loss

                # Take gradient steps
                self.actor_optimizer.zero_grad()
                self.critic_optimizer.zero_grad()
                total_loss.backward()
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
