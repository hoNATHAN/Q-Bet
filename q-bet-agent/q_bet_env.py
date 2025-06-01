import gym 
import numpy as np
from gym import spaces
from agent_utils import load_data, load_raw_matches
from training import lookup_winner

class QBetEnv(gym.Env):
    metadata = {'render.modes': []}
    def __init__(self, states=None):
        super().__init__()
        self.matches = states if states is not None else load_data()
        self.raw_json = load_raw_matches()
        self.match_idx = 0
        self.round_idx = 0
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(19, ), dtype=np.float32)
        self.action_space = spaces.Discrete(3)
        self.current_balance = 1000.0

    def reset(self, *, match_idx: int = 0):
        self.current_balance = 1000.0
        self.match_idx = match_idx
        self.round_idx = 0
        return self.matches[self.match_idx][0][2].cpu().numpy()

    def step(self, action):
        match_id, game_idx, state = self.matches[self.match_idx][self.round_idx]
        winner = lookup_winner(match_id, game_idx)
        mj = self.raw_json[match_id]["games"][f"game{game_idx + 1}"]
        match_rounds = self.matches[self.match_idx]
        local_count = sum(
            1
            for (mid, g_idx, _) in match_rounds[: self.round_idx]
            if g_idx == game_idx
        )
        round_key = f"round_{local_count + 1}"

        round_info = mj["rounds"][round_key]
        a_odds = float(round_info.get("team_a_odds", 1.0))
        b_odds = float(round_info.get("team_b_odds", 1.0))

        if action == 2:
            reward = 0.0
        elif action == winner:
            odds = a_odds if action == 0 else b_odds
            reward = odds - 1.0
        else:
            reward = -1.0

        self.current_balance += reward
        info = {"balance": self.current_balance}

        self.round_idx += 1
        done = (
            self.round_idx >= len(self.matches[self.match_idx])
            or self.current_balance <= 0
        )
        obs = (
            np.zeros(self.observation_space.shape, dtype=np.float32)
            if done
            else state.cpu().numpy()
        )

        return obs, reward, done, info


    def render(self, mode='human'):
        pass

    