import json
import torch

# TODO: enumerate the maps
MAPS = ["train", "dust2", "mirage", "inferno"]

# TODO: enumerate buy types
BUY_TYPES = ["Eco", "Semi", "Full", "Force"]


def process_state(json_str):
    data = json.loads(json_str)


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
    "rounds": 17,
    "map": "train",
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
    },
  }
"""
