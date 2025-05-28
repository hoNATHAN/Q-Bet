import json
import os


with open('../bo3_tournament_data.json', 'r') as f:
    data = json.load(f)

odds_files = [
    "odds_3dmax-vs-big-22-04-2025.json",
    "odds_3dmax-vs-gamerlegion-21-04-2025.json",
    "odds_complexity-gaming-vs-gamerlegion-22-04-2025.json",
    "odds_falcons-vs-navi-22-04-2025.json",
    "odds_falcons-vs-saw-21-04-2025.json",
    "odds_falcons-vs-team-vitality-27-04-2025.json",
    "odds_faze-clan-vs-3dmax-22-04-2025.json",
    "odds_faze-clan-vs-gamerlegion-23-04-2025.json",
    "odds_faze-clan-vs-pain-gaming-20-04-2025.json",
    "odds_faze-clan-vs-the-mongolz-21-04-2025.json",
    "odds_gamerlegion-vs-falcons-25-04-2025.json",
    "odds_gamerlegion-vs-mouz-21-04-2025.json",
    "odds_mouz-vs-big-21-04-2025.json",
    "odds_mouz-vs-falcons-26-04-2025.json",
    "odds_mouz-vs-the-mongolz-23-04-2025.json",
    "odds_navi-vs-flyquest-22-04-2025.json",
    "odds_navi-vs-mibr-21-04-2025.json",
    "odds_navi-vs-team-liquid-23-04-2025.json",
    "odds_pain-gaming-vs-complexity-gaming-21-04-2025.json",
    "odds_saw-vs-mibr-22-04-2025.json",
    "odds_team-liquid-vs-mibr-23-04-2025.json",
    "odds_team-liquid-vs-team-vitality-22-04-2025.json",
    "odds_team-liquid-vs-virtus.pro-21-04-2025.json",
    "odds_team-vitality-vs-falcons-23-04-2025.json",
    "odds_team-vitality-vs-flyquest-21-04-2025.json",
    "odds_team-vitality-vs-the-mongolz-26-04-2025.json",
    "odds_the-mongolz-vs-complexity-gaming-20-04-2025.json",
    "odds_the-mongolz-vs-team-liquid-25-04-2025.json",
    "odds_virtus.pro-vs-flyquest-22-04-2025.json",
]



# Extract all match names from all tournaments
match_teams = set()
for tournament in data.values():
    for match in tournament.get("matches", []):
        match_base = "-".join(match["match_name"].split("-")[:-3])
        if "-vs-" in match_base:
            team1, team2 = match_base.split("-vs-")
            match_teams.add(team1)
            match_teams.add(team2)

# Print or use the list
print(sorted(match_teams))

unique_teams = set() 
directory_path = './../data/odds/'  # Replace with your actual directory path

odds_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
for match in odds_files:
    # Remove date at the end
    match_base = "-".join(match.split("-")[:-3])
    # Split teams by '-vs-'
    if "-vs-" in match_base:
        team1, team2 = match_base.split("-vs-")
        unique_teams.add(team1)
        unique_teams.add(team2)

# Print sorted list of teams
print(sorted(unique_teams))

