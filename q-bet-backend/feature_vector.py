import json
import torch
import numpy as np

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


def one_hot(value, categories):
    ohe_vector = np.zeros(len(categories))
    ohe_vector[categories[value]] = 1

    return ohe_vector


# elif isinstance(value, str):


# TODO: consider pandas json normalize
# figure out what values need to be divided
def append_game_features(d, features):
    for key, value in d.items():
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
            else:
                print("unknown dictionary handling error")
        elif isinstance(value, (int, float)):
            if key == "initial_team_a_econ" or key == "initial_team_b_econ":
                features.append(float(value) / MAX_ECON)
            elif key == "buy_team_a_econ" or key == "buy_team_b_econ":
                features.append(float(value) / MAX_ECON)
            elif key == "final_team_a_econ" or key == "final_team_b_econ":
                features.append(float(value) / MAX_ECON)
            elif key == "duration":
                features.append(float(value) / MAX_ROUND_TIME)
        else:
            print("unknown entry encountered")
            pass


def process_state(json_str):
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

    return final_feature_vector


def main():
    process_state(sample_state_json)


if __name__ == "__main__":
    main()
