"""
Credit to https://github.com/nikhilbarhate99/PPO-PyTorch/blob/master/PPO.py
"""

import torch
import numpy as np
import torch.nn as nn
from torch.distributions import MultivariateNormal, Categorical

################################## set device ##################################
print("============================================================================================")
device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda:0")
    torch.cuda.empty_cache()
    print("Device set to : " + str(torch.cuda.get_device_name(device)))
else:
    print("Device set to : cpu")
print("============================================================================================")


################################## PPO Policy ##################################
class RolloutBuffer:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.state_values = []
        self.is_terminals = []

    def clear(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.state_values[:]
        del self.is_terminals[:]


class ActorCritic(nn.Module):
    def __init__(
        self, state_dim, action_dim, has_continuous_action_space, action_std_init
    ):
        super(ActorCritic, self).__init__()

        self.has_continuous_action_space = has_continuous_action_space

        # Flag to detect "complex_discrete" vs "basic" discrete vs continuous
        self.is_complex_discrete = False

        if has_continuous_action_space:
            # Continuous action: output a vector of length action_dim, each ∈ [0,1]
            self.action_dim = action_dim
            self.action_var = torch.full(
                (action_dim,), action_std_init * action_std_init
            ).to(device)

            self.actor = nn.Sequential(
                nn.Linear(state_dim, 64),
                nn.Tanh(),
                nn.Linear(64, 64),
                nn.Tanh(),
                nn.Linear(64, action_dim),
                nn.Sigmoid(),  # ensures output ∈ [0,1]
            )

        else:
            # Discrete action: "basic" if action_dim == 3, else "complex_discrete"
            if action_dim == 3:
                # Basic discrete: Softmax over 3 actions (bet A, bet B, abstain)
                self.actor = nn.Sequential(
                    nn.Linear(state_dim, 64),
                    nn.Tanh(),
                    nn.Linear(64, 64),
                    nn.Tanh(),
                    nn.Linear(64, action_dim),
                    nn.Softmax(dim=-1),
                )
            else:
                # Complex discrete: action_dim = 3 + N
                N = action_dim - 3
                self.side_head = nn.Sequential(
                    nn.Linear(state_dim, 64),
                    nn.Tanh(),
                    nn.Linear(64, 64),
                    nn.Tanh(),
                    nn.Linear(64, 3),
                    nn.Softmax(dim=-1),
                )
                self.stake_head = nn.Sequential(
                    nn.Linear(state_dim, 64),
                    nn.Tanh(),
                    nn.Linear(64, 64),
                    nn.Tanh(),
                    nn.Linear(64, N),
                    nn.Softmax(dim=-1),
                )
                self.is_complex_discrete = True

        # Critic (common to all cases)
        self.critic = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )

    def set_action_std(self, new_action_std):
        if self.has_continuous_action_space:
            self.action_var = torch.full(
                (self.action_dim,), new_action_std * new_action_std
            ).to(device)
        else:
            print("--------------------------------------------------------------------------------------------")
            print("WARNING : Calling ActorCritic::set_action_std() on discrete action space policy")
            print("--------------------------------------------------------------------------------------------")

    def forward(self):
        raise NotImplementedError

    def act(self, state):
        if self.has_continuous_action_space:
            # Continuous branch: Gaussian 
            action_mean = self.actor(state)
            action_mean = torch.nan_to_num(action_mean, nan=0.0, posinf=0.0, neginf=0.0)
            cov_mat = torch.diag(self.action_var)  # use shape (D, D)
            dist = MultivariateNormal(action_mean, cov_mat)
            action = dist.sample()
            action_logprob = dist.log_prob(action)
            state_val = self.critic(state)
            return action.detach(), action_logprob.detach(), state_val.detach()

        else:
            # Discrete branch
            if not self.is_complex_discrete:
                # Basic discrete: single Softmax over epsilon
                action_probs = self.actor(state)
                action_probs = torch.nan_to_num(action_probs, nan=1e-8, posinf=1e-8, neginf=1e-8)
                dist = Categorical(action_probs)
                action = dist.sample()
                action_logprob = dist.log_prob(action)
                state_val = self.critic(state)
                return action.detach(), action_logprob.detach(), state_val.detach()

            else:
                # Complex discrete: two-headed Softmax
                side_probs = self.side_head(state)
                side_probs = torch.nan_to_num(side_probs, nan=1e-8, posinf=1e-8, neginf=1e-8)
                side_dist = Categorical(side_probs)
                side_idx = side_dist.sample()
                lp_side = side_dist.log_prob(side_idx)

                stake_probs = self.stake_head(state)
                stake_probs = torch.nan_to_num(stake_probs, nan=1e-8, posinf=1e-8, neginf=1e-8)
                stake_dist = Categorical(stake_probs)
                stake_idx = stake_dist.sample()
                lp_stake = stake_dist.log_prob(stake_idx)

                # Combine log-probs for joint action
                action_logprob = lp_side + lp_stake
                state_val = self.critic(state)

                action = torch.stack([side_idx.float(), stake_idx.float()]).long()
                return action.detach(), action_logprob.detach(), state_val.detach()

    def evaluate(self, state, action):
        if self.has_continuous_action_space:
            mean = self.actor(state)
            mean = torch.nan_to_num(mean, nan=0.0, posinf=0.0, neginf=0.0)
            cov_mat = torch.diag(self.action_var)
            dist = MultivariateNormal(mean, cov_mat)
            action_logprobs = dist.log_prob(action)
            dist_entropy = dist.entropy()
            state_values = self.critic(state)
            return action_logprobs, state_values, dist_entropy

        else:
            if not self.is_complex_discrete:
                # Basic discrete evaluate
                action_probs = self.actor(state)
                action_probs = torch.nan_to_num(action_probs, nan=1e-8, posinf=1e-8, neginf=1e-8)
                dist = Categorical(action_probs)
                action_logprobs = dist.log_prob(action)
                dist_entropy = dist.entropy()
                state_values = self.critic(state)
                return action_logprobs, state_values, dist_entropy

            else:
                # Complex discrete evaluate: `action` shape = (batch, 2)
                side_idx = action[:, 0].long()
                stake_idx = action[:, 1].long()

                side_probs = self.side_head(state)
                stake_probs = self.stake_head(state)
                side_probs = torch.nan_to_num(side_probs, nan=1e-8, posinf=1e-8, neginf=1e-8)
                stake_probs = torch.nan_to_num(stake_probs, nan=1e-8, posinf=1e-8, neginf=1e-8)

                dist_side = Categorical(side_probs)
                dist_stake = Categorical(stake_probs)

                lp_side = dist_side.log_prob(side_idx)
                lp_stake = dist_stake.log_prob(stake_idx)
                action_logprobs = lp_side + lp_stake
                dist_entropy = dist_side.entropy() + dist_stake.entropy()
                state_values = self.critic(state)
                return action_logprobs, state_values, dist_entropy


class PPO:
    def __init__(
        self,
        state_dim,
        action_dim,
        lr_actor,
        lr_critic,
        gamma,
        K_epochs,
        eps_clip,
        has_continuous_action_space,
        action_std_init=0.6,
        device: torch.device = device
    ):
        self.has_continuous_action_space = has_continuous_action_space
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if has_continuous_action_space:
            self.action_std = action_std_init

        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs

        self.buffer = RolloutBuffer()

        # Main policy network
        self.policy = ActorCritic(
            state_dim, action_dim, has_continuous_action_space, action_std_init
        ).to(self.device)


        if hasattr(self.policy, "is_complex_discrete") and self.policy.is_complex_discrete:
            actor_params = list(self.policy.side_head.parameters()) + list(self.policy.stake_head.parameters())
        else:
            actor_params = self.policy.actor.parameters()

        self.optimizer = torch.optim.Adam(
            [
                {"params": actor_params,    "lr": lr_actor},
                {"params": self.policy.critic.parameters(), "lr": lr_critic},
            ]
        )

        # Old policy (for sampling and ratio)
        self.policy_old = ActorCritic(
            state_dim, action_dim, has_continuous_action_space, action_std_init
        ).to(self.device)
        self.policy_old.load_state_dict(self.policy.state_dict())

        self.MseLoss = nn.MSELoss()
        self.last_update_metrics = {}

    def set_action_std(self, new_action_std):
        if self.has_continuous_action_space:
            self.action_std = new_action_std
            self.policy.set_action_std(new_action_std)
            self.policy_old.set_action_std(new_action_std)
        else:
            print("--------------------------------------------------------------------------------------------")
            print("WARNING : Calling PPO::set_action_std() on discrete action space policy")
            print("--------------------------------------------------------------------------------------------")

    def decay_action_std(self, action_std_decay_rate, min_action_std):
        print("--------------------------------------------------------------------------------------------")
        if self.has_continuous_action_space:
            self.action_std = self.action_std - action_std_decay_rate
            self.action_std = round(self.action_std, 4)
            if self.action_std <= min_action_std:
                self.action_std = min_action_std
                print("setting actor output action_std to min_action_std : ", self.action_std)
            else:
                print("setting actor output action_std to : ", self.action_std)
            self.set_action_std(self.action_std)
        else:
            print("WARNING : Calling PPO::decay_action_std() on discrete action space policy")
        print("--------------------------------------------------------------------------------------------")

    def select_action(self, state):
        """
        Samples an action from the old policy.
        Returns:
          - a length-2 NumPy array [side_idx, stake_idx] when complex_discrete,
          - a scalar int when basic,
          - a NumPy array of floats when continuous.
        """
        # (1) Move state → device, sanitize
        with torch.no_grad():
            if isinstance(state, torch.Tensor):
                state = state.to(self.device)
            else:
                state = torch.FloatTensor(state).to(self.device)
            state = torch.nan_to_num(state, nan=0.0, posinf=0.0, neginf=0.0)

            # (2) Sample action from old policy
            action, action_logprob, state_val = self.policy_old.act(state)

        # (3) Store in buffer
        self.buffer.states.append(state)
        self.buffer.actions.append(action)
        self.buffer.logprobs.append(action_logprob)
        self.buffer.state_values.append(state_val)

        # (4) Return according to action space
        if self.has_continuous_action_space:
            arr = action.detach().cpu().numpy().flatten()
            return np.clip(arr, 0.0, 1.0)

        # Discrete: if action tensor has more than one element → complex_discrete
        if action.numel() > 1:
            return action.detach().cpu().numpy().astype(np.int64)

        # Otherwise: basic discrete
        return action.item()

    def update(self):
        # Monte Carlo estimate of returns
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(
            reversed(self.buffer.rewards), reversed(self.buffer.is_terminals)
        ):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)

        # Normalizing the rewards
        rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        if rewards.numel() > 1:
            rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-7)
        else:
            rewards = rewards - rewards.mean()

        if len(self.buffer.states) < 2:
            self.buffer.clear()
            return

        old_states = (
            torch.squeeze(torch.stack(self.buffer.states, dim=0)).detach().to(self.device)
        )
        old_actions = (
            torch.squeeze(torch.stack(self.buffer.actions, dim=0)).detach().to(self.device)
        )
        old_logprobs = (
            torch.squeeze(torch.stack(self.buffer.logprobs, dim=0)).detach().to(self.device)
        )
        old_state_values = (
            torch.squeeze(torch.stack(self.buffer.state_values, dim=0))
            .detach()
            .to(self.device)
        )

        # calculate advantages
        advantages = rewards.detach() - old_state_values.detach()

        ret_mean = rewards.mean().item()
        ret_std = rewards.std(unbiased=False).item() if rewards.numel() > 1 else 0.0

        # Optimize policy for K epochs
        for _ in range(self.K_epochs):
            logprobs, state_values, dist_entropy = self.policy.evaluate(
                old_states, old_actions
            )

            state_values = torch.squeeze(state_values)
            ratios = torch.exp(logprobs - old_logprobs.detach())

            surr1 = ratios * advantages
            surr2 = (
                torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            )

            p_loss = -torch.min(surr1, surr2).mean()  # policy loss
            v_loss = 0.5 * self.MseLoss(state_values, rewards)
            ent = dist_entropy.mean()  # entropy loss

            loss = p_loss + v_loss - 0.01 * ent

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            avg_p_loss = p_loss.item()
            avg_v_loss = v_loss.item()
            avg_entropy = ent.item()

        avg_p_loss /= self.K_epochs
        avg_v_loss /= self.K_epochs
        avg_entropy /= self.K_epochs

        # Copy new weights into old policy
        self.policy_old.load_state_dict(self.policy.state_dict())
        # clear buffer
        self.buffer.clear()

        self.last_update_metrics = {
            "return_mean": ret_mean,
            "return_std": ret_std,
            "policy_loss": avg_p_loss,
            "value_loss": avg_v_loss,
            "entropy": avg_entropy,
        }

    def save(self, checkpoint_path):
        torch.save(self.policy_old.state_dict(), checkpoint_path)

    def load(self, checkpoint_path):
        self.policy_old.load_state_dict(
            torch.load(checkpoint_path, map_location=lambda storage, loc: storage)
        )
        self.policy.load_state_dict(
            torch.load(checkpoint_path, map_location=lambda storage, loc: storage)
        )
