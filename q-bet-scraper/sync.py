from datetime import datetime, timedelta
import json
from pprint import pprint
import os
from Levenshtein import jaro_winkler

def get_curr_odds(timestamp_list, team, team_curr_odds, curr_time, odds_data):
    curr_odds = team_curr_odds
    while True and len(timestamp_list) > 0:
        most_recent_time = timestamp_list[0]
        if most_recent_time <= curr_time:
            curr_odds = odds_data[team][most_recent_time.strftime("%Y-%m-%d %H:%M")][0]
            timestamp_list.pop(0)
        else:
            break
    return curr_odds

#odds_file = "odds_astralis-vs-team-spirit-18-05-2025.json"
#match_file = "match_astralis-vs-spirit-18-05-2025.json"

def match_team(team, odds_teams):
    print(odds_teams)
    best_team = None
    best_similarity = -1

    for odds_team in odds_teams:
        distance = jaro_winkler(team, odds_team)
        if distance > best_similarity:
            best_similarity = distance
            best_team = odds_team

    print(f"{team} {best_team}")
    odds_teams.remove(best_team)
    return best_team


def sync(odds_file, match_file, sync_path):
    time_after_game = 7
    time_after_round = 5

    with open(odds_file, 'r') as f:
        odds_data = json.load(f)

    with open(match_file, 'r') as f:
        match_data = json.load(f)

    start_time = match_data["start_time"]
    num_games = match_data["game_count"]
    match_id = match_data["match_id"]
    year = 2025
    if "2024" in match_id:
        year = 2024
    start_datetime = datetime.strptime(start_time, "%b %d, %H:%M").replace(year=year)


    '''Sort the odds timestamps for both teams'''
    #team_a = "astralis"
    #team_b = "team-spirit"
    odds_teams = list(odds_data.keys())
    team_a = match_team(match_data["team_a"], odds_teams)
    team_b = match_team(match_data["team_b"], odds_teams)
    team_a_keys = odds_data[team_a].keys()
    team_a_datetime_keys = [datetime.strptime(k, "%Y-%m-%d %H:%M").replace(year=year) for k in team_a_keys]
    team_a_sorted_datetime_keys = sorted(team_a_datetime_keys)

    team_b_keys = odds_data[team_b].keys()
    team_b_datetime_keys = [datetime.strptime(k, "%Y-%m-%d %H:%M").replace(year=year) for k in team_b_keys]
    team_b_sorted_datetime_keys = sorted(team_b_datetime_keys)

    '''Get the current odds closest to start time'''
    team_a_curr_odds = get_curr_odds(team_a_sorted_datetime_keys, team_a, "", start_datetime, odds_data)
    team_b_curr_odds = get_curr_odds(team_b_sorted_datetime_keys, team_b, "", start_datetime, odds_data)

    curr_time = start_datetime
    for x in range(num_games):
        game = match_data[f"game{x+1}"]
        num_rounds = game["rounds"]
        for y in range(num_rounds):
            curr_round = game[f"round_{y+1}"]
            duration = curr_round["duration"]
            curr_time = curr_time + timedelta(seconds=duration)
            team_a_curr_odds = get_curr_odds(team_a_sorted_datetime_keys, team_a, team_a_curr_odds, curr_time, odds_data)
            team_b_curr_odds = get_curr_odds(team_b_sorted_datetime_keys, team_b, team_b_curr_odds, curr_time, odds_data)
            curr_round["team_a_odds"] = team_a_curr_odds
            curr_round["team_b_odds"] = team_b_curr_odds
            curr_time = curr_time + timedelta(seconds=5) # Apparently there are 5 seconds in between rounds

        curr_time = curr_time + timedelta(minutes=10) # Assume there are 10 minutes in between games

    
    filename = os.path.basename(match_file)
    file_name = filename[6:]
    with open(f'{sync_path}full_{file_name}.json', 'w') as f:  
        json.dump(match_data, f, indent=2)  

def find_odds_file(match_file, odds_path):
    odds_files = [f[5:] for f in os.listdir(odds_path) if os.path.isfile(os.path.join(odds_path, f))]
    best_file = None
    best_similarity = -1

    for f in odds_files:
        distance = jaro_winkler(match_file, f)
        if distance > best_similarity and distance > 0.9:
            best_similarity = distance
            best_file = f

    return f"odds_{best_file}"

if __name__ == "__main__":

    match_path = "./data/match/"
    odds_path = "./data/odds/"
    sync_path = "./data/full/"

    match_files = [f for f in os.listdir(match_path) if os.path.isfile(os.path.join(match_path, f))]
    for match_file in match_files:
        fixed_match_file = match_file[6:]
        odds_file = find_odds_file(fixed_match_file, odds_path)
        if odds_file == "odds_None":
            continue
        print(f"Syncing {match_file} and {odds_file}")
        sync(f"{odds_path}{odds_file}", f"{match_path}{match_file}", sync_path)


