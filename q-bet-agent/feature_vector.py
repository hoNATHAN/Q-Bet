# @title Feature Vector Util
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
from typing import List, Optional, Tuple
import torch
import numpy as np

BUY_TYPES = {"eco": 0, "semi": 1, "full": 2, "force": 3}

# investigate
WIN_TYPES = {
    "ace": 0,
    "defuse": 1,
    "explode": 2,
    "timeout": 3,
}

WINNER = {
    "team a": 0,
    "team b": 1,
}


MAX_ECON = 16000


# round time and rounds capped for 95th percentile of data
MAX_ROUND_TIME = 300  # seconds
MAX_ROUNDS = 24.0  # regulation rounds in CS2, first to 16 wins up to 30
ROI_CAP = 24.0


MAX_PLAYERS = 5.0


def safe_lower(val):
    return str(val).strip().lower()


def ohe(value, categories):
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
    try:
        ohe_vector[categories[safe_lower(value)]] = 1
    except ValueError:
        raise ValueError("Caught an unknown type", value, categories)

    return ohe_vector


def parse_american_odds(s: str) -> float:
    """
    Turn American odds string to a float.
    "+150" -> 150
    "-200" -> -200

    Parameters:
        s (str): The American odds string to convert.

    Returns:
        float: The converted float value.
    """
    s = str(s).strip().lstrip("+")
    try:
        return float(s)
    except ValueError:
        return 0.0


def am_to_decimal(american_odds: float) -> float:
    """
    Convert American odds to decimal odds.

    Parameters:
        american_odds (float): The American odds to convert.

    Returns:
        float: The corresponding decimal odds.
    """
    if american_odds > 0:
        return american_odds / 100.0 + 1.0
    else:
        return 1.0 - 100.0 / american_odds


def signed_log_norm(x, cap=ROI_CAP):
    return np.sign(x) * np.log1p(np.abs(x)) / (np.log1p(cap) + 1e-6)


def append_game_features(d: dict, features: list, ev=False):
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

    # pull econ stats for team a and b
    init_a_econ, buy_a_econ, final_a_econ = (
        float(d["initial_team_a_econ"]),
        float(d["buy_team_a_econ"]),
        float(d["final_team_a_econ"]),
    )
    init_b_econ, buy_b_econ, final_b_econ = (
        float(d["initial_team_b_econ"]),
        float(d["buy_team_b_econ"]),
        float(d["final_team_b_econ"]),
    )

    delta_a_econ = (final_a_econ - init_a_econ) / MAX_ECON
    delta_b_econ = (final_b_econ - init_b_econ) / MAX_ECON

    # add delta econ for team a and b
    features.extend([delta_a_econ, delta_b_econ])

    # calculate ROI for a and b
    # add epsilon to denominator to avoid divide by 0
    roi_a = (final_a_econ - init_a_econ + buy_a_econ) / (buy_a_econ + 1e-6)
    roi_b = (final_b_econ - init_b_econ + buy_b_econ) / (buy_b_econ + 1e-6)

    norm_roi_a = signed_log_norm(roi_a)
    norm_roi_b = signed_log_norm(roi_b)

    # add ROI for team a and b
    # normalize as 0, 1 if wanted
    # features.extend([(norm_roi_a + 1) / 2.0, (norm_roi_b + 1) / 2.0])
    features.extend([norm_roi_a, norm_roi_b])

    # append player kills normalized
    a_kills, b_kills = d["kills_end"]["team_a"], d["kills_end"]["team_b"]
    features.extend([a_kills / MAX_PLAYERS, b_kills / MAX_PLAYERS])

    # cost per kill
    # divide by zero guard with epsilon
    cpk_a = buy_a_econ / max(a_kills, 1)
    cpk_b = buy_b_econ / max(b_kills, 1)
    features.extend([cpk_a / MAX_ECON, cpk_b / MAX_ECON])

    # odds features
    raw_odds_a = parse_american_odds(d["team_a_odds"])
    raw_odds_b = parse_american_odds(d["team_b_odds"])
    raw_odds_a = raw_odds_a if abs(raw_odds_a) > 1e-6 else 1e-6
    raw_odds_b = raw_odds_b if abs(raw_odds_b) > 1e-6 else 1e-6
    odds_a, odds_b = am_to_decimal(raw_odds_a), am_to_decimal(raw_odds_b)
    features.extend([min(odds_a, 10) / 10, min(odds_b, 10) / 10])

    # implied probabilities
    p_a, p_b = 1 / odds_a, 1 / odds_b
    tot = p_a + p_b
    features.extend([p_a / tot, p_b / tot])

    # odds-ROI or profit fraction
    features.extend([(odds_a - 1) / odds_a, (odds_b - 1) / odds_b])

    # normalize and append duration
    clipped_duration = min(float(d["duration"]), MAX_ROUND_TIME)
    features.append(clipped_duration / MAX_ROUND_TIME)

    # append winner
    features.extend(ohe(d["winner"], WINNER))

    # cumulative score
    sa, sb = map(float, d["score"].split("-"))
    features.extend([sa / MAX_ROUNDS, sb / MAX_ROUNDS])

    # two extra features are added if EV is set to true
    # EV of teams
    # Kelly Criterion for teams
    if ev:
        ev_a = p_a * (odds_a - 1) - (1 - p_a)
        ev_b = p_b * (odds_b - 1) - (1 - p_b)

        kelly_a = 0.0 if ev_a <= 0 else ev_a / (odds_a - 1)
        kelly_b = 0.0 if ev_b <= 0 else ev_b / (odds_b - 1)
        features.extend([ev_a, ev_b, kelly_a, kelly_b])


def process_state(json_str: str) -> Optional[List[Tuple[str, int, torch.Tensor]]]:
    """
    Parses a game state JSON string, extracts round-level features from game1 round_1,
    applies normalization and encoding, and converts the result into a PyTorch tensor.

    Parameters:
        json_str (str): A string containing JSON-formatted match data.

    Returns:
        list of torch.Tensor: A 1D tensor containing the normalized feature vector.
    """
    failed = None
    try:
        # load json data
        data = json.loads(json_str)

        if not isinstance(data, dict):
            raise ValueError("Top-level JSON is not an object")

        games = data["games"]
        feature_states = []
        failed = data

        for game_idx, (_, value) in enumerate(games.items()):
            rounds = value["rounds"]
            if not isinstance(rounds, dict):
                raise ValueError("Missing or invalid 'rounds' field")

            for round_idx, (_, value) in enumerate(rounds.items()):
                feature_vector = []

                append_game_features(value, feature_vector)

                final_feature_vector = torch.tensor(feature_vector, dtype=torch.float32)
                feature_states.append(
                    (data["match_id"], game_idx, final_feature_vector)
                )

                #  or round_idx == len(rounds.items()) - 1
                # if round_idx == 0:
                #     print("\nRound:", round_idx + 1)
                #     print("Cardinality:", len(feature_vector))
                #     print(" Raw Feature Vector:\n", feature_vector, "\n")
                #     print(" Final Feature Vector:\n", final_feature_vector, "\n\n")

        return feature_states

    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
        print(f"Error in process_state: {e}")
        print(failed)
        return None


"""
Final Feature Vector of Cardinality 19 dimensions

Features Pulled:
 - Δ-econ A, B (2d)
 - ROI A, B (2d)
 - Kills A, B (2d)
 - Decimal odds A, B (2d)
 - Implied-prob A, B (2d)
 - Odds-ROI A, B (2d)
 - Duration (1d)
 - Winner flag A, B (2d)

--- Game: Intel Extreme Masters Melbourne 2025 ---


Round: 1
Cardinality: 19
 Raw Feature Vector:
 [0.9, 0.41875, np.float64(1.0121845991223732), np.float64(0.7798450741608249), 1.0, 0.4, 0.0075, 0.0203125, 0.16993006993006993, 0.20400000000000001, 0.5455565529622981, 0.4544434470377019, 0.4115226337448559, 0.5098039215686274, 0.4266666666666667, np.float64(1.0), np.float64(0.0), 0.041666666666666664, 0.0] 

 Final Feature Vector:
 tensor([0.9000, 0.4187, 1.0122, 0.7798, 1.0000, 0.4000, 0.0075, 0.0203, 0.1699,
        0.2040, 0.5456, 0.4544, 0.4115, 0.5098, 0.4267, 1.0000, 0.0000, 0.0417,
        0.0000]) 

"""
