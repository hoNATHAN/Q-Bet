import os
import json
from pprint import pprint

def move_games(data):
    num_games = data["game_count"]
    data["games"] = {}
    for x in range(1, num_games+1):
        curr_game = data[f"game{x}"]
        data["games"][f"game{x}"] = curr_game
        del data[f"game{x}"]

def move_rounds(data):
    num_games = data["game_count"]
    for x in range(1, num_games+1):
        curr_game = data["games"][f"game{x}"]
        num_rounds = curr_game["rounds"]
        curr_game["total_rounds"] = num_rounds
        data["games"][f"game{x}"]["rounds"] = {}

        for y in range(1, num_rounds+1):
            curr_round = curr_game[f"round_{y}"]
            data["games"][f"game{x}"]["rounds"][f"round_{y}"] = curr_round
            del data["games"][f"game{x}"][f"round_{y}"]

if __name__ == "__main__":

    full_path = "./data/full/"
    v1_path = "./data/v1/"

    full_files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]

    for f in full_files:
        with open(f"{full_path}{f}", 'r') as x:
            data = json.load(x)
        move_games(data)
        move_rounds(data)
        num_games = data["game_count"]
        for x in range(1, num_games+1):
            num_rounds = data["games"][f"game{x}"]["total_rounds"]
            for y in range(1, num_rounds+1):
                team_a_odds = data["games"][f"game{x}"]["rounds"][f"round_{y}"]["team_a_odds"]
                while team_a_odds.count('-') > 1:
                    team_a_odds = team_a_odds.replace('-', '', 1)
                data["games"][f"game{x}"]["rounds"][f"round_{y}"]["team_a_odds"] = team_a_odds

                team_b_odds = data["games"][f"game{x}"]["rounds"][f"round_{y}"]["team_b_odds"]
                while team_b_odds.count('-') > 1:
                    team_b_odds = team_b_odds.replace('-', '', 1)
                data["games"][f"game{x}"]["rounds"][f"round_{y}"]["team_b_odds"] = team_b_odds

                del data["games"][f"game{x}"]["rounds"][f"round_{y}"]["weapons_end"]
                del data["games"][f"game{x}"]["rounds"][f"round_{y}"]["players_alive_end"]


        with open(f'{v1_path}v1_{f[5:]}', 'w') as x:  
            json.dump(data, x, indent=2)  
