import gym 
import numpy as np
from gym import spaces
from agent_utils import load_data, load_match_json
from training import lookup_winner, compute_reward

class QBetEnv(gym.Env):
    metadata = {'render.modes': []}
    def __init__(self, states=None):
        super().__init__()
        self.matches = states or load_data()
        self.mathc_idx = 0
        self.round_idx = 0

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(19, ), dtype=np.float32)
        self.action_space = spaces.Discrete(3)

    def reset(self, *, match_idx: int = 0):
        self.match_idx = match_idx
        self.round_idx = 0
        _, _, state = self.matches[self.match_idx][self.round_idx]
        return state.cpu().numpy()
    
    def step(self, action):
        match_id, game_idx, state = self.matches[self.match_idx][self.round_idx]
        winner = lookup_winner(match_id, game_idx)
        reward = compute_reward(action, winner)
        self.round_idx += 1
        done = self.round_idx >= len(self.matches[self.match_idx])
        observation = (np.zeros(self.observation_space.shape, dtype=np.float32)
                       if done
                       else self.matches[self.match_idx][self.round_idx][2].cpu().numpy())
        return observation, reward, done, {}
    
    def render(self, mode='human'):
        pass

    