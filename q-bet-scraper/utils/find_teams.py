import json

with open('tournament_data.json', 'r') as f:
    data = json.load(f)

teams = []

for key in data.keys():
    matches = data[key]["matches"]
    for match in matches:
        name = match["match_name"]
        stripped = name.rsplit("-", 3)[0]
        team1, team2 = stripped.split("-vs-")
        if team1 not in teams:
            teams.append(team1)
        if team2 not in teams:
            teams.append(team2)
print(teams)
print(len(teams))
