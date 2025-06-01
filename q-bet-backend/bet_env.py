"""
Filename: bet_env.py
Author: Alexey Kuraev
Date: 2025-05-26
Version: 1.0
Description:
    This script defines a custom Gym environment for the Q-Bet agent.
Dependencies: gym, numpy, feature_vector, action_space
"""

import gym
from gym import spaces
import numpy as np
import os
import json
from feature_vector import process_state, sample_state_json
from action_space import ACTION_SPACE_SIZE, BET_PERCENTAGES

#change this is we change where the data is stored
FOLDER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'q-bet-scraper', 'data', 'full'))

def load_match_json(file):
    tensor_states_for_one_match = []
    if file.endswith('.json'):
        file_path = os.path.join(FOLDER_PATH, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                match_data = f.read()
                states = process_state(match_data)
                if states is not None:
                    tensor_states_for_one_match.extend(states)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return tensor_states_for_one_match


def load_data():
    tensor_states = []
    for root, _, files in os.walk(FOLDER_PATH):
        for file in files:
            tensor_states.append(load_match_json(file))
    return tensor_states

class BettingEnv(gym.Env):
    """
    Custom Gym environment for betting on cs2 matches.

    Parameters:
        gym.Env: parent class for all Gym environments.

    Returns:
        BettingEnv: an instance of the BettingEnv class.
    """
    metadata = {'render.modes': ['human']} #not sure if we need the render mode, but if we do imma leave it here

    def __init__(self, initial_balance=1000, max_steps=50):
        super(BettingEnv, self).__init__()
        dummy_state = process_state(sample_state_json)
        state_shape = dummy_state.numpy().shape
        self.observation_space = spaces.Box(low=-np.inf, high=-np.inf,
                                            shape=state_shape, dtype=np.float32)
        self.bet_actions = [(None, 0.0)] + [('A', p) for p in [0.05,0.10,0.25,0.50,0.75,1.00]] + [('B', p) for p in [0.05,0.10,0.25,0.50,0.75,1.00]]
        self.action_space = spaces.Discrete(len(self.bet_actions))
        self.initial_balance = initial_balance
        self.max_steps = max_steps
        self.current_balance = None
        self.state = None
        self.step_count = None
        self.match_files = sorted(
            os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH) if f.endswith('.json')
        )
        self.match_idx = 0
        self.round_idx = 0

    def reset(self):
        if self.match_idx >= len(self.match_files):
            raise IndexError("No more matches to load")
        self.current_balance = self.initial_balance
        self.step_count = 0
        self._load_current_match()
        self.state = self._get_state()
        return self.state

    def step(self, action):
        team, bet_pct = self.bet_actions[action]
        if team is None:
            reward = 0.0
        else:
            bet_amount = self.current_balance * bet_pct
            if team == 'A':
                payout_odds = self.odds_a[self.round_idx]
                win = (self.winners[self.round_idx] == 'team a')
            else:
                payout_odds = self.odds_b[self.round_idx]
                win = (self.winners[self.round_idx] == 'team b')

            reward = bet_amount * (payout_odds - 1) if win else -bet_amount

        self.current_balance += reward
        self.round_idx += 1
        self.step_count += 1

        done = (self.round_idx >= len(self.rounds) or self.current_balance <= 0 or self.step_count >= self.max_steps)

        if done:
            self.match_idx += 1
            next_state = None
        else:
            next_state = self._get_state()
            self.state = next_state

        info = {'balance': self.current_balance, 'payout_odds': payout_odds}
        return self.state, reward, done, info

    def render(self, mode='human'):
        print(f"Step: {self.step_count}, Balance: {self.current_balance}")

    def _load_current_match(self):
        """Load synced full match JSON with embedded odds across all games and rounds"""
        file_path = self.match_files[self.match_idx]
        with open(file_path, 'r', encoding='utf-8') as f:
            match_data = json.load(f)
        games = match_data.get('games', {})
        all_rounds, odds_a, odds_b, winners = [], [], [], []
        for game_key in sorted(games.keys(), key=lambda x: int(x.replace('game',''))): 
            game = games[game_key]
            game_map = game.get('map')
            rounds_dict = game.get('rounds', {})
            for rnd_key in sorted(rounds_dict.keys(), key=lambda x: int(x.split('_')[1])):
                rd = rounds_dict[rnd_key]
                rd['map'] = game_map
                all_rounds.append(rd)
                odds_a.append(rd.get('team_a_odds', 1.0))
                odds_b.append(rd.get('team_b_odds', 1.0))
                winners.append(rd.get('winner', '').lower())
        self.rounds = all_rounds
        self.odds_a = odds_a
        self.odds_b = odds_b
        self.winners = winners
        self.round_idx = 0

    def _get_state(self): #iffy on this one, migth be wrong
        """Generate the observation array for the current round"""
        round_data = self.rounds[self.round_idx]
        game = {'map': round_data.get('map'), 'rounds': {'round_1': round_data}}
        json_str = json.dumps({'games': {'game1': game}})
        state_tensor = process_state(json_str)
        return state_tensor.numpy()


