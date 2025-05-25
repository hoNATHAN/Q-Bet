import json
from collections import defaultdict

# Replace this with your full tournament JSON input
input_json = {
    "PGL Astana 2025": {
        "url": "https://bo3.gg/tournaments/pgl-astana-2025/results",
        "matches": [
            {
                "match_name": "example",
                "match_url": "https://example.com"
            }
        ]
    }
    # Add more tournaments here...
}

with open('../bo3_tournament_data.json') as f:
    input_json = json.load(f)

# Predefined group definitions
grouped_tournaments = {
    "Group 1": [
        "ESL Pro League Season 20", "PGL Bucharest 2025", "ESL Pro League Season 21 Play-in",
        "YaLLa Compass 2024", "IEM Rio 2024", "Intel Extreme Masters Melbourne 2025",
        "IEM Cologne 2024", "BLAST Premier: Spring Groups 2024",
        "Intel Extreme Masters Katowice 2025 Play-In", "BLAST Premier: Spring Final 2024",
        "BLAST Premier: Fall Final 2024", "BetBoom Dacha Belgrade 2024 #2 Play-in"
    ],
    "Group 2": [
        "ESL Pro League Season 19", "ESL Pro League Season 21", "Perfect World Shanghai Major 2024",
        "Skyesports Championship 2024", "IEM Dallas 2024", "IEM Katowice 2024",
        "CCT Global Finals 2024", "Esports World Cup 2024", "IEM Cologne 2024 Play-in",
        "IEM Katowice 2024 Play-in", "BLAST Premier: World Final 2024",
        "Thunderpick World Championship 2024", "BLAST Bounty Spring 2025"
    ],
    "Group 3": [
        "PGL Cluj-Napoca 2025", "PGL Astana 2025", "PGL Major Copenhagen 2024",
        "Perfect World Shanghai Major 2024 Opening", "BLAST Open Spring 2025",
        "IEM Chengdu 2024", "Intel Extreme Masters Katowice 2025",
        "BLAST Premier: Fall Groups 2024", "Thunderpick World Championship 2024 Play-in",
        "BetBoom Dacha Belgrade 2024 #2", "BLAST Rivals Spring 2025", "BetBoom Dacha Belgrade 2024"
    ]
}

def split_tournaments_by_group(tournament_json, group_definitions):
    grouped_output = defaultdict(dict)
    for tournament_name, tournament_data in tournament_json.items():
        for group_name, tournaments in group_definitions.items():
            if tournament_name in tournaments:
                grouped_output[group_name][tournament_name] = tournament_data
                break
    return grouped_output

# Split the input into groups
grouped_data = split_tournaments_by_group(input_json, grouped_tournaments)
with open(f'1.json', 'w') as f:  
    json.dump(grouped_data["Group 1"], f, indent=2)  
with open(f'2.json', 'w') as f:  
    json.dump(grouped_data["Group 2"], f, indent=2)  
with open(f'3.json', 'w') as f:  
    json.dump(grouped_data["Group 3"], f, indent=2)  

# Optional: print result
#print(json.dumps(grouped_data, indent=2))

