"""
File: match_winner_lookup.py
Author: Nathan Ho
Date: 2025-05-30
Description:
    Scans a directory of match JSON files and builds a lookup table mapping
    each match_id to a dictionary of game_name → last_round_winner. Writes the
    resulting lookup JSON to a specified output path.
"""

import os
import glob
import json


def build_match_winner_lookup(folder_path):
    """
    Scans all .json files under the given folder_path and constructs a lookup
    dictionary in the form:
        {
            match_id: {
                game_name: last_round_winner,
                ...
            },
            ...
        }

    For each JSON file:
      - Attempts to load it.
      - Uses 'match_id' from the file content (or filename if missing).
      - Iterates through each 'game' in data["games"], sorts its rounds by
        numeric suffix, and records the 'winner' from the last round.

    Parameters:
        folder_path (str): Path to the directory containing match JSON files.

    Returns:
        dict: A mapping from each match_id to its per-game last-round winner data.
    """
    lookup = {}
    for filepath in glob.glob(os.path.join(folder_path, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Skipping {filepath}: {e}")
            continue

        match_id = (
            data.get("match_id") or os.path.splitext(os.path.basename(filepath))[0]
        )
        games = data.get("games", {})
        game_winners = {}

        for game_name, game in games.items():
            rounds = game.get("rounds", {})
            if not rounds:
                continue

            # sort the rounds by their numeric suffix
            def round_number(rk):
                # rk is like "round_1", "round_12"
                try:
                    return int(rk.split("_", 1)[1])
                except (IndexError, ValueError):
                    return 0

            sorted_rounds = sorted(
                rounds.items(), key=lambda item: round_number(item[0])
            )
            _, last_round_data = sorted_rounds[-1]
            winner = last_round_data.get("winner")
            game_winners[game_name] = winner

        lookup[match_id] = game_winners

    return lookup


if __name__ == ("__main__"):
    folder_path = "../data/"
    folder = folder_path + "v1/"
    winners = build_match_winner_lookup(folder)

    with open(folder_path + "winners/match_winners.json", "w", encoding="utf-8") as out:
        json.dump(winners, out, indent=2)
    print("Built lookup for", len(winners), "matches")
