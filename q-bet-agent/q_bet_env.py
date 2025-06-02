# q_bet_env.py

import gym
import numpy as np
from gym import spaces
from agent_utils import load_data, load_raw_matches
from training import lookup_winner

class QBetEnv(gym.Env):
    """
    Custom Gym environment for Q-Bet agent betting on CS2 matches.

    Each “episode” is one match (multiple games/rounds), and at each timestep the agent chooses
    how much (and on which team) to bet. Rewards update the agent's “bankroll” and are computed
    according to the chosen scheme (basic, binary, or complex).
    """

    metadata = {'render.modes': []}
    def __init__(self, states=None, reward_scheme='basic', action_space_type='basic', basic_fraction=1.0, initial_balance=1000.0):
        super().__init__()

        # If `states` is already a list of matches (each match is a list of (mid,game_idx,state)), use it directly.
        if states is not None and states and isinstance(states[0], list):
            self.matches = states
        else:
            # group flat list of (match_id, game_idx, state) tuples into per-match episodes
            raw_states = states if states is not None else load_data()
            match_dict = {}
            for mid, game_idx, st in raw_states:
                match_dict.setdefault(mid, []).append((mid, game_idx, st))
            self.matches = list(match_dict.values())

        self.raw_json = load_raw_matches()
        self.match_idx = 0
        self.round_idx = 0

        #configuration flags
        self.reward_scheme = reward_scheme
        self.action_space_type = action_space_type
        # fraction of bankroll to bet when using basic action space
        self.basic_fraction = basic_fraction
        # initial bankroll balance
        self.initial_balance = initial_balance

        #define discrete stakes for complex_discrete, capped at 50% of bankroll
        self.discrete_stakes = [0.10, 0.20, 0.30, 0.40, 0.50]
        # dynamically infer observation_space from first round's feature vector
        if not self.matches or not self.matches[0]:
            raise RuntimeError("Cannot infer observation_space: no state vectors provided")
        _, _, sample_state = self.matches[0][0]
        feat_dim = sample_state.shape[0]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(feat_dim,), dtype=np.float32
        )

        #action space setup: basic, complex_discrete, complex_continuous
        if action_space_type == 'basic':
            #0 = bet A, 1 = bet B, 2 = abstain
            self.action_space = spaces.Discrete(3)
        elif action_space_type == 'complex_discrete':
            N = len(self.discrete_stakes)
            #two‐headed MultiDiscrete: [side in {0,1,2}, stake_idx in {0..N-1}]
            self.action_space = spaces.MultiDiscrete([3, N])
        else:  # complex_continuous
            #two floats in [0,1]: frac_a, frac_b
            self.action_space = spaces.Box(
                low=0.0, high=1.0, shape=(2,), dtype=np.float32
            )

        self.current_balance = self.initial_balance

    def _decode_action(self, action):
        """
        Decode 'action' into (frac_a, frac_b) according to action_space_type.

        - If action_space_type == 'basic', `action` is an int ∈ {0,1,2}.
        - If action_space_type == 'complex_discrete', `action` is a length-2 array: [side_idx, stake_idx].
        - If action_space_type == 'complex_continuous', `action` is a length-2 float array: [frac_a, frac_b].
        """
        if self.action_space_type == 'basic':
            # bet a fixed fraction of bankroll on one side or abstain
            if action == 0:
                return self.basic_fraction, 0.0   #bet fraction on Team A
            elif action == 1:
                return 0.0, self.basic_fraction   #bet fraction on Team B
            else:
                return 0.0, 0.0   #abstain

        if self.action_space_type == 'complex_discrete':
            #action must be a length 2 array
            side_idx  = int(action[0])
            stake_idx = int(action[1])
            if side_idx == 2:
                #abstain
                return 0.0, 0.0
            elif side_idx == 0:
                #bet team A at fraction discrete_stakes[stake_idx]
                return self.discrete_stakes[stake_idx], 0.0
            else:
                #bet team B at fraction discrete_stakes[stake_idx]
                return 0.0, self.discrete_stakes[stake_idx]

        #complex_continuous: action is [frac_a, frac_b]
        frac_a, frac_b = action
        return float(frac_a), float(frac_b)

    def _basic_reward(self, action: int, outcome: int, #makes no sense dont pass basic for reward
                      a_odds: float, b_odds: float) -> float:
        """
        BASIC: 
          if action == 2        -> 0.0
          elif action == outcome -> (odds - 1.0)
          else                  -> -1.0
        """
        if action == 2:
            return 0.0
        elif action == outcome:
            odds = a_odds if action == 0 else b_odds
            return odds - 1.0
        else:
            return -1.0

    def _binary_reward(self, action: int, outcome: int,
                       stake_a: float, stake_b: float) -> float:
        """
        BINARY: 
          +1 if you bet the correct side (regardless of magnitude),
          -1 if you bet incorrectly,
          0 if you abstained.
        """
        total_stake = stake_a + stake_b
        if total_stake == 0.0:
            return 0.0
        chosen = 0 if stake_a > stake_b else 1
        return 1.0 if chosen == outcome else -1.0

    def _complex_reward(self, outcome: int,
                        stake_a: float, stake_b: float,
                        a_odds: float, b_odds: float) -> float:
        """
        COMPLEX: true dollar P/L based on fractional stake:
          bet_amount = (stake_fraction x current_balance)
          if correct:  profit = (odds - 1.0) x bet_amount
          if wrong:    loss   = -bet_amount
        """
        prev_balance = self.current_balance
        total_stake = stake_a + stake_b

        #if abstained or if already bankrupt, P/L = 0
        if total_stake == 0.0 or prev_balance <= 0.0:
            return 0.0

        chosen = 0 if stake_a > stake_b else 1
        if chosen == outcome:
            #win: (odds−1) * stake
            if chosen == 0:
                return (a_odds - 1.0) * stake_a
            else:
                return (b_odds - 1.0) * stake_b
        else:
            #lose: −(stake)
            return -total_stake

    def reset(self, *, match_idx: int = 0):
        self.current_balance = self.initial_balance
        self.match_idx = match_idx
        self.round_idx = 0
        return self.matches[self.match_idx][0][2].cpu().numpy()

    def step(self, action):
        """
        1. Decode action -> fractional stakes
        2. Compute raw_reward according to chosen reward_scheme
        3. Clip that raw_reward to ±1000 to keep balance from exploding
        4. Update balance by the CLIPPED reward
        5. Return (obs, clipped_reward, done, info)
        """
        #get the match id, game index, and state for the current round
        match_id, game_idx, state = self.matches[self.match_idx][self.round_idx]

        #lookup the winner of the game
        winner = lookup_winner(match_id, game_idx)
#------------------------------------------------------------------------------------------------can be a function 
        #get the match json and round info
        mj = self.raw_json[match_id]["games"][f"game{game_idx + 1}"]
        match_rounds = self.matches[self.match_idx]

        #count how many rounds have been played in this match up to now
        local_count = sum(
            1
            for (mid, g_idx, _) in match_rounds[: self.round_idx]
            if g_idx == game_idx
        )
        #get the round info for the current round
        round_key = f"round_{local_count + 1}"
        round_info = mj["rounds"][round_key]

        #safely parse odds: default = 1.0 if missing/invalid
        def _get_odds(key):
            val = round_info.get(key, 1.0)
            try:
                return float(val)
            except (ValueError, TypeError):
                return 1.0
#------------------------------------------------------------------------------------------------
        #calculate the odds for team A and team B
        a_odds = _get_odds("team_a_odds")
        b_odds = _get_odds("team_b_odds")

        #decode the action into fractional stakes
        frac_a, frac_b = self._decode_action(action)

        #if the total fraction is greater than 1.0, normalize it so we never bet more than 100%
        total_frac = frac_a + frac_b
        if total_frac > 1.0 and total_frac > 0.0:
            frac_a /= total_frac
            frac_b /= total_frac

        #calculate the stakes based on the current balance
        stake_a = frac_a * self.current_balance
        stake_b = frac_b * self.current_balance

        #compute the reward based on the chosen reward scheme
        if self.reward_scheme == 'basic':
            raw_reward = self._basic_reward(
                action if self.action_space_type == 'basic'
                else (0 if stake_a > stake_b else 1 if stake_b > stake_a else 2),
                winner, a_odds, b_odds
            )
        elif self.reward_scheme == 'binary':
            raw_reward = self._binary_reward(
                action if self.action_space_type == 'basic'
                else (0 if stake_a > stake_b else 1 if stake_b > stake_a else 2),
                winner, stake_a, stake_b
            )
        else:  #complex
            raw_reward = self._complex_reward(winner, stake_a, stake_b, a_odds, b_odds)

        #clip the reward to precent crazy balance swings
        clipped_reward = float(np.clip(raw_reward, -1000.0, +1000.0))
        self.current_balance += clipped_reward

        info = {
            "balance": self.current_balance,
            "stake_a": stake_a,
            "stake_b": stake_b,
            "a_odds": a_odds,
            "b_odds": b_odds,
        }

        self.round_idx += 1
        done = (
            self.round_idx >= len(self.matches[self.match_idx])
            or self.current_balance <= 0.0
        )
        obs = (
            np.zeros(self.observation_space.shape, dtype=np.float32)
            if done
            else state.cpu().numpy()
        )

        return obs, clipped_reward, done, info
