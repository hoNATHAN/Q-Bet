import json
import torch
import numpy

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
        "weapons_end": {
            "team_a": {
            "AK": 0,
            "M4": 0,
            "AWP": 0
            },
            "team_b": {
            "AK": 0,
            "M4": 0,
            "AWP": 0
            }
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
MAPS_ENUM = {
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

BUY_TYPE_ENUM = {"Eco": 0, "Semi": 1, "Full": 2, "Force": 3}

WIN_TYPE_ENUM = {
    "ace": 0,
    "defuse": 1,
    "planted": 2,
}

WINNER_ENUM = {
    "Team A": 0,
    "Team B": 1,
}


# TODO: consider if this is needed
MAX_ECON = 16000
MAX_ROUNDS = 16  # maybe 24? or indefinite

# includes buy + round + bomb
MAX_ROUND_TIME = 195  # seconds
MAX_GAME_TIME = 2400  # seconds


# TODO: consider pandas json normalize
# figure out what values need to be divided
def append_game_features(d, features):
    for key, value in d.items():
        if isinstance(value, dict):
            append_game_features(value, features)
        elif isinstance(value, (int, float)):
            features.append(float(value))
        elif isinstance(value, str):
            if key == "team_a_buy_type" or key == "team_b_buy_type":
                features.append(
                    BUY_TYPE_ENUM.get(value, -1)
                )  # TODO: use -1 or some default for unknown
            elif key == "win_type":
                features.append(WIN_TYPE_ENUM.get(value, -1))
            elif key == "winner":
                features.append(WINNER_ENUM.get(value, -1))
            elif key == "score":
                print("score found")
                score = list(map(int, value.split("-")))
                features.append(score[0] / MAX_ROUNDS)
                features.append(score[1] / MAX_ROUNDS)
            else:
                pass
        else:
            # ignore other types or handle accordingly
            pass


def process_state(json_str):
    # load json data
    data = json.loads(json_str)

    game = data["game1"]
    map = game["map"]
    rounds = game["rounds"]

    # TODO: iterate and pull game state
    round_data = rounds["round_1"]

    features = []

    append_game_features(round_data, features)
    features.append(MAPS_ENUM.get(map, -1))

    print(features)


def main():
    process_state(sample_state_json)


if __name__ == "__main__":
    main()
