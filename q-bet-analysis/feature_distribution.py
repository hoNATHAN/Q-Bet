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
import seaborn as sns

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
    percentile_95 = float(np.percentile(durations, 95))
    print(percentile_95)
    plt.hist(durations, bins=30, alpha=0.7)
    plt.axvline(percentile_95, color="red", linestyle="--", label="95th Percentile")
    plt.title("Distribution of Round Durations")
    plt.xlabel("Duration (seconds)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig("round_duration_dist.pdf", bbox_inches="tight")
    plt.show()

    rounds_arr = np.array(all_rounds)
    rounds_mean = rounds_arr.mean()
    rounds_std = rounds_arr.std()
    rounds_95 = float(np.percentile(rounds_arr, 95))

    print("\n--- ROUNDS ---")
    print("Mean:", rounds_mean)
    print("Std:", rounds_std)
    print("95th Percentile:", rounds_95)

    plt.figure()
    plt.hist(rounds_arr, bins=100, alpha=0.7)
    plt.axvline(rounds_95, color="red", linestyle="--", label="95th Percentile")
    plt.xlabel("Rounds")
    plt.ylabel("Frequency")
    plt.title("Distribution of Rounds in a Match")
    plt.legend()
    plt.savefig("rounds_distribution.pdf", bbox_inches="tight")
    plt.close()

    # === ROIs ===
    rois_arr = np.array(all_rois)
    rois_mean = rois_arr.mean()
    rois_std = rois_arr.std()
    rois_99 = float(np.percentile(rois_arr, 99))

    sns.violinplot(x=rois_arr)
    plt.title("Violin Plot of Team's ROI")
    plt.xlabel("ROI")
    plt.savefig("roi_violin.pdf", bbox_inches="tight")
    plt.show()

    print("\n--- ROIS ---")
    print("Mean:", rois_mean)
    print("Std:", rois_std)
    print("99th Percentile:", rois_99)

    plt.figure()
    plt.hist(rois_arr, bins=100, alpha=0.7)
    plt.axvline(rois_99, color="red", linestyle="--", label="99th Percentile")
    plt.xlabel("ROI")
    plt.ylabel("Frequency")
    plt.title("Distribution of ROIs")
    plt.legend()
    plt.savefig("roi_distribution.pdf", bbox_inches="tight")
    plt.show()
