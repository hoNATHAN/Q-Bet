import json

with open('../bo3_tournament_data.json', 'r') as f:
    data = json.load(f)

teams = []

for key in data.keys():
    matches = data[key]["matches"]
    print(f"{key}: {len(matches)}")
