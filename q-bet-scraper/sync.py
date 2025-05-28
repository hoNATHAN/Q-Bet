from datetime import datetime, timedelta
import json
from pprint import pprint
import os
from Levenshtein import jaro_winkler
import re

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
    team = team.lower()
    best_team = None
    best_similarity = -1

    for odds_team in odds_teams:
        distance = jaro_winkler(team, odds_team)
        in_name = 0
        if team in odds_team:
            in_name += 1

        score = distance + in_name
        if score > best_similarity:
            best_similarity = score
            best_team = odds_team

    #print(f"{team} {best_team}")
    #odds_teams.remove(best_team)
    return best_team


def sync(odds_file, match_file, sync_path):
    time_after_game = 7
    time_after_round = 5
    #print(odds_file)
    #print(match_file)

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
    if "2024" in start_time or "2025" in start_time:
        start_datetime = datetime.strptime(start_time, "%b %d, %Y %H:%M").replace(year=year)
    else:
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
    try:
        team_a_curr_odds = get_curr_odds(team_a_sorted_datetime_keys, team_a, "", start_datetime, odds_data)
        team_b_curr_odds = get_curr_odds(team_b_sorted_datetime_keys, team_b, "", start_datetime, odds_data)
    except:
        print(f"Error Syncing {match_file} and {odds_file}")
        return False


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
    with open(f'{sync_path}full_{file_name}', 'w') as f:  
        json.dump(match_data, f, indent=2)  


TEAM_MAP = {
    '3dmax': '3dmax',
    '9-pandas': '9-pandas',
    '9z': '9z-team',
    'alternate-attax-cs-go': 'd',  # No odds
    'amkal': 'amkal-esports',
    'apeks': 'apeks',
    'astralis': 'astralis',
    'atox': 'atox',
    'aurora-gaming': 'aurora',
    'bad-news-kangaroos': 'odds_bad-news-kangaroos',
    'bestia': 'bestia',
    'betboom': 'betboom-team',
    'betboom-20': 'betboom-team',  # assuming variant
    'betboom-team': 'betboom-team',
    'betclic-apogee-esports': 'apogee',
    'big': 'big',
    'bleed-esports-cs': 'bleed-esports',
    'boss': '',  # appears only in odds_ list
    'cloud9': 'cloud9',
    'complexity': 'complexity-gaming',
    'ecstatic': 'ecstatic',
    'ence': 'ence',
    'eternal-fire': 'eternal-fire',
    'falcons-esports': 'falcons',
    'faze': 'faze-clan',
    'flyquest': 'flyquest',
    'fnatic': 'fnatic',
    'forze': 'forze',
    'furia': 'furia',
    'future': 'dms',
    'g2': 'g2-esports',
    'gaimingladiators': 'gaimin-gladiators',
    'gamerlegion': 'gamerlegion',
    'heroic': 'heroic',
    'hotu': 'hotu',
    'housebets': '',  # educated guess
    'imperial': 'imperial',
    'imperial-female': 'imperial-w',
    'jijiehao': 'odds_jijiehao',
    'legacy-br': 'legacy',
    'liquid': 'team-liquid',
    'lynn-vision': 'lynn-vision',
    'm80-cs-go': 'm80',
    'mibr': 'mibr',
    'mindfreak': '',  # weak match
    'monte': 'monte',
    'mousesports': 'mouz',
    'natus-vincere': 'navi',
    'nemiga': 'nemiga-gaming',
    'nip': 'ninjas-in-pyjamas',
    'nrg': 'nrg-esports',
    'oddik': 'oddik',
    'og': 'og',
    'pain-gaming': 'pain-gaming',
    'parivision': 'parivision',
    'passion-ua': 'passion-ud',  # best approximation
    'pera': '',  # ambiguous, closest guess
    'rare-atom': 'rare-atom',
    'rebels-gaming-cs': 'odds_red-canids',
    'red-canids-cs-go': 'red-canids',
    'revenant-cs': 'revenant-esports',
    'rooster': 'rooster',
    'sangal': '',  # no exact match
    'sashi-esport': 'sashi',
    'saw': 'saw',
    'spirit': 'team-spirit',
    'steel-helmet': 'steel-helmet',
    'the-huns-esports': 'the-huns',
    'the-mongolz': 'the-mongolz',
    'themongolz': 'the-mongolz',
    'true-rippers': 'true-rippers',
    'tyloo-cs-go': 'tyloo',
    'virtus-pro': 'virtus.pro',
    'vitality': 'team-vitality',
    'wildcard-gaming': 'wildcard-gaming'
}

def normalize_filename(filename):
    for long, short in TEAM_MAP.items():
        filename = filename.replace(long, short)
    return filename

def reverse_teams_in_filename(filename):
    """
    Reverses the order of teams in a filename containing 'teamA-vs-teamB'.

    Example:
        'match_astralis-vs-spirit-18-05-2025.json' → 'match_spirit-vs-astraslis-18-05-2025.json'
    """
    match = re.search(r"(.*?)([a-z0-9\.\-]+)-vs-([a-z0-9\.\-]+)(-\d{2}-\d{2}-\d{4}\.json)", filename)
    if match:
        prefix, team1, team2, suffix = match.groups()
        return f"{prefix}{team2}-vs-{team1}{suffix}"
    else:
        return filename


def decrement_date_in_filename(filename):
    """
    Decrease the date in a filename by one day.

    Example:
    'match_astralis-vs-spirit-18-05-2025.json' → 'match_astralis-vs-spirit-17-05-2025.json'
    """
    match = re.search(r"(\d{2}-\d{2}-\d{4})", filename)
    if not match:
        return filename  # No date found, return as-is

    date_str = match.group(1)
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        new_date = date_obj - timedelta(days=1)
        new_date_str = new_date.strftime("%d-%m-%Y")
        return filename.replace(date_str, new_date_str)
    except ValueError:
        return filename  # If date parsing fails, return as-is

def find_odds_file(match_file, odds_files):
    threshold = 0.95
    match_ext = match_file[-12:-5]
    date_matches = [f for f in odds_files if match_ext in f]
    match_norm = normalize_filename(match_file)

    # --- 1. Try normal team order ---
    for f in date_matches:
        distance = jaro_winkler(match_norm[:-12], f[5:-12])
        if distance == 1.0:
            return f

    # --- 2. Try reversed team order ---
    match_norm_reverse = reverse_teams_in_filename(match_norm)
    for f in date_matches:
        distance = jaro_winkler(match_norm_reverse[:-12], f[5:-12])
        if distance == 1.0:
            return f

    # --- 3. Try normal decrement ---
    match_norm_decrement = decrement_date_in_filename(match_norm)
    for f in date_matches:
        distance = jaro_winkler(match_norm_decrement[:-12], f[5:-12])
        if distance == 1.0:
            return f

    # --- 3. Try normal decrement ---
    match_norm_decrement_reverse = decrement_date_in_filename(match_norm_reverse)
    for f in date_matches:
        distance = jaro_winkler(match_norm_decrement_reverse[:-12], f[5:-12])
        if distance == 1.0:
            return f

    return None



if __name__ == "__main__":

    match_path = "./data/match/"
    odds_path = "./data/odds/"
    sync_path = "./data/full/"

    match_files = [f for f in os.listdir(match_path) if os.path.isfile(os.path.join(match_path, f))]
    odds_files = [f for f in os.listdir(odds_path) if os.path.isfile(os.path.join(odds_path, f))]

    print(len(odds_files))
    counter = 0
    for match_file in match_files:
        curr_match_file = match_file
        fixed_match_file = curr_match_file[6:]
        curr_odds_file = find_odds_file(fixed_match_file, odds_files)
        if curr_odds_file is None:
            print(f"Failed Syncing {curr_match_file} and {curr_odds_file}")
        else:
            odds_files.remove(curr_odds_file)
            #match_files.remove(curr_match_file)
            #print(f"Syncing {curr_match_file} and {curr_odds_file}")
            sync(f"{odds_path}{curr_odds_file}", f"{match_path}{curr_match_file}", sync_path)
            counter += 1
    #print(counter)
    print(len(odds_files))
            


    '''
    for match_file in match_files:
        fixed_match_file = match_file[6:]
        odds_file = find_odds_file(fixed_match_file, odds_path)
        if odds_file == "odds_None":
            continue
        print(f"Syncing {match_file} and {odds_file}")
        sync(f"{odds_path}{odds_file}", f"{match_path}{match_file}", sync_path)
    print(tochi)
    '''


