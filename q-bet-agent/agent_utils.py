# @title Json File Parse
import os
from feature_vector import process_state
import json


def load_match_json(file):
    tensor_states_for_one_match = []
    if file.endswith(".json"):
        file_path = os.path.join(matches_path, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                match_data = f.read()
                state = process_state(match_data)
                if state is not None:  # check to avoid breakage
                    tensor_states_for_one_match.extend(state)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return tensor_states_for_one_match


def load_data():
    tensor_states = []
    for root, _, files in os.walk(matches_path):
        for file in files:
            tensor_states.append(load_match_json(file))
    return tensor_states


def load_raw_matches():
    raw = {}
    for fn in os.listdir(matches_path):
        if fn.endswith(".json"):
            path = os.path.join(matches_path, fn)
            j = json.load(open(path, "r"))
            mid = j["match_id"]
            raw[mid] = j
    return raw

# path to matches json
matches_path = "../data/v1"

# path to winners json
winners_path = "../data/winners/match_winners.json"
