"""
File: feature_distribution.py
Author: Nathan Ho
Date: 2025-05-30
Description:
    Parses a directory of match JSON files in parallel to extract:
      - Round durations
      - Number of rounds per game
      - ROI values for each team in each round
    Then computes and plots summary statistics (mean, standard deviation, percentiles)
    for durations, rounds, and ROIs.
"""

import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import matplotlib.pyplot as plt

all_durations = []
all_rounds = []
all_rois = []


def parse_file(path: str):
    """
    Read a single JSON match file and extract:
      - durations: list of round durations
      - round_counts: list containing the number of rounds in each game
      - rois: list of ROI values for Team A and Team B in each round

    Parameters:
        path (str): File path to a match JSON file.

    Returns:
        tuple:
            durations (list[float]): Duration of every round across all games.
            round_counts (list[int]): Number of rounds per game.
            rois (list[float]): ROI values computed for each team in each round.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            match = json.load(f)
    except Exception:
        return [], [], []

    durs = []
    round_counts = []
    rois = []
    for game in match.get("games", {}).values():
        rounds = game.get("rounds", {})
        round_counts.append(len(rounds))
        for rd in rounds.values():
            # Duration
            durs.append(rd["duration"])

            # ROI for Team A
            ia = float(rd["initial_team_a_econ"])
            ba = float(rd["buy_team_a_econ"])
            fa = float(rd["final_team_a_econ"])
            rois.append((fa - ia + ba) / (ba + 1e-6))

            # ROI for Team B
            ib = float(rd["initial_team_b_econ"])
            bb = float(rd["buy_team_b_econ"])
            fb = float(rd["final_team_b_econ"])
            rois.append((fb - ib + bb) / (bb + 1e-6))

    return durs, round_counts, rois


if __name__ == "__main__":
    folder_path = "../data/v1"

    file_paths = []
    for root, _, files in os.walk(folder_path):
        for fn in files:
            if fn.endswith(".json"):
                file_paths.append(os.path.join(root, fn))

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(parse_file, fp): fp for fp in file_paths}
        for fut in as_completed(futures):
            durs, rounds, rs = fut.result()
            all_durations.extend(durs)
            all_rounds.extend(rounds)
            all_rois.extend(rs)

    durations = np.array(all_durations)
    print("--- DURATIONS ---")
    print("Mean:", durations.mean())
    print("Std:", durations.std())
    print("95th Percentile:", np.percentile(durations, 95))
    plt.hist(durations, bins=100)
    plt.xlabel("Duration")
    plt.ylabel("Frequency")
    plt.title("Distribution of Durations")
    plt.show()

    rounds_arr = np.array(all_rounds)
    print("\n--- ROUNDS ---")
    print("Mean:", rounds_arr.mean())
    print("Std:", rounds_arr.std())
    print("95th Percentile:", np.percentile(rounds_arr, 95))
    plt.hist(rounds_arr, bins=100)
    plt.xlabel("Rounds")
    plt.ylabel("Frequency")
    plt.title("Distribution of Rounds")
    plt.show()

    rois_arr = np.array(all_rois)
    print("\n--- ROIS ---")
    print("Mean:", rois_arr.mean())
    print("Std:", rois_arr.std())
    print("99th Percentile:", np.percentile(rois_arr, 99))
    plt.hist(rois_arr, bins=100)
    plt.xlabel("ROI")
    plt.ylabel("Frequency")
    plt.title("Distribution of ROIs")
    plt.show()
