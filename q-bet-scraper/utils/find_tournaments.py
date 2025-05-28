import json

with open('tournament_data.json', 'r') as f:
    data = json.load(f)

teams = []

for key in data.keys():
    print(key)
