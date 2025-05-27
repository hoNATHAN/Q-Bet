"""
Filename: feature_vector.py
Author: Nathan Ho
Date: 2025-05-24
Version: 1.0
Description:
    This script has functions that takes in a game state
    and maps it to a feature vector as a pytorch tensor
Dependencies: json, torch, numpy, time
"""

import json
import torch
import numpy as np
import time

sample_state_json = """
{
  "tournament": "PGL Astana 2025",
  "team_a": "FURIA",
  "team_b": "MIBR",
  "status": "Ended",
  "start_time": "May 12, 01:00",
  "link": "https://bo3.gg/matches/furia-vs-mibr-12-05-2025",
  "match_id": "furia-vs-mibr-12-05-2025",
  "game_count": 3,
  "game1": {
    "round_num": 17,
    "map": "train",
    "rounds": {
        "round_1": {
            "initial_team_a_econ": 4000,
            "initial_team_b_econ": 4000,
            "buy_team_a_econ": 600,
            "buy_team_b_econ": 600,
            "final_team_a_econ": 18400,
            "final_team_b_econ": 10600,
            "winner": "Team A",
            "win_type": "ace",
            "duration": 122,
            "team_a_buy_type": "Eco",
            "team_b_buy_type": "Eco",
            "score": "1-0",
            "players_alive_end": {
                "team_a": 0,
                "team_b": 0
            },
            "kills_end": {
                "team_a": 5,
                "team_b": 2
            },
            "assists_end": {
                "team_a": 0,
                "team_b": 0
            }
        }
    }
  }
}
"""

# TODO: include unknown maps
MAPS = {
    "train": 0,
    "ancient": 1,
    "anubis": 2,
    "dust2": 3,
    "inferno": 4,
    "mirage": 5,
    "nuke": 6,
    "overpass": 7,
    "office": 8,
    "vertigo": 9,
    "basalt": 10,
    "edin": 11,
    "italy": 12,
}

BUY_TYPES = {"Eco": 0, "Semi": 1, "Full": 2, "Force": 3}

WIN_TYPES = {
    "ace": 0,
    "defuse": 1,
    "planted": 2,
}

WINNER = {
    "Team A": 0,
    "Team B": 1,
}


# TODO: consider if this is needed
MAX_ECON = 16000
MAX_ROUNDS = 16  # maybe 24? or indefinite

# includes buy + round + bomb
MAX_ROUND_TIME = 155  # seconds

# should we have a different max for bomb wins timers ?
MAX_ROUND_TIME_BOMB = 155  # seconds
MAX_GAME_TIME = 2400  # seconds

MAX_PLAYERS = 5.0


def one_hot(value, categories):
    """
    Converts a categorical string value into a one-hot encoded numpy array
    based on a provided category-to-index mapping.

    Parameters:
        value (str): The categorical value to encode.
        categories (dict): A dictionary mapping category names to integer indices.

    Returns:
        np.ndarray: A one-hot encoded numpy array representing the category.
    """

    ohe_vector = np.zeros(len(categories))
    ohe_vector[categories[value]] = 1

    return ohe_vector


# TODO: consider pandas json normalize
# figure out what values need to be divided
def append_game_features(d, features):
    """
    Extracts and encodes features from a single game round dictionary,
    and appends them to the provided feature list.

    Handles:
        - Categorical string values via one-hot encoding.
        - Numerical values via normalization.
        - Dictionary-type values (like player stats) via normalization of subfields.

    Parameters:
        d (dict): A dictionary containing game round data.
        features (list): A list to which processed numerical features are appended.
    """

    for key, value in d.items():
        # Handles single string categorical data
        if isinstance(value, str):
            if key == "team_a_buy_type" or key == "team_b_buy_type":
                features.extend(one_hot(value, BUY_TYPES))
            elif key == "win_type":
                features.extend(one_hot(value, WIN_TYPES))
            elif key == "winner":
                features.extend(one_hot(value, WINNER))
            elif key == "score":
                score = list(map(int, str(value).split("-")))
                features.append(score[0] / MAX_ROUNDS)
                features.append(score[1] / MAX_ROUNDS)
        # Normalizes numerical input
        elif isinstance(value, (int, float)):
            if key == "initial_team_a_econ" or key == "initial_team_b_econ":
                features.append(float(value) / MAX_ECON)
            elif key == "buy_team_a_econ" or key == "buy_team_b_econ":
                features.append(float(value) / MAX_ECON)
            elif key == "final_team_a_econ" or key == "final_team_b_econ":
                features.append(float(value) / MAX_ECON)
            elif key == "duration":
                features.append(float(value) / MAX_ROUND_TIME)
        # Handles dictionary types like player stats
        elif isinstance(value, dict):
            if key == "players_alive_end" or key == "kills_end" or key == "assists_end":
                for item in value.items():
                    features.append(float(item[1]) / MAX_PLAYERS)


def process_state(json_str):
    """
    Parses a game state JSON string, extracts round-level features from game1 round_1,
    applies normalization and encoding, and converts the result into a PyTorch tensor.

    Parameters:
        json_str (str): A string containing JSON-formatted match data.

    Returns:
        torch.Tensor: A 1D tensor containing the normalized feature vector.
    """

    # load json data
    data = json.loads(json_str)

    game = data["game1"]
    map = game["map"]
    rounds = game["rounds"]

    # TODO: iterate and pull game state
    round_data = rounds["round_1"]

    feature_vector = []

    append_game_features(round_data, feature_vector)
    feature_vector.extend(one_hot(map, MAPS))

    print("Raw Feature Vector: \n", feature_vector, "\n")

    final_feature_vector = torch.tensor(feature_vector, dtype=torch.float32)
    print("Final Feature Vector: \n", final_feature_vector, "\n")

    # TODO: use as a return
    return final_feature_vector


def main():
    start_time = time.time()
    process_state(sample_state_json)
    print("--- Feature Vector Performance: %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()
