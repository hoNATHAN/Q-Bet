"""
File: generate_graph.py
Author: Matt Protacio
Date: 2025-06-01
Description:
    Takes a csv file and generates graphs based on the columns
"""

import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt

def average_reward_graph(csv_file):
    csv_df = pd.read_csv(csv_file)
    avg_rewards = csv_df.groupby("episode")["reward"].mean().reset_index()
    avg_rewards.rename(columns={"reward": "average_reward"}, inplace=True)
    plt.figure(figsize=(10,6))
    plt.plot(avg_rewards["episode"], avg_rewards["average_reward"], marker='o')
    plt.title("Average Reward vs. Episode")
    plt.xlabel("Episode")
    plt.ylabel("Average Reward")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == ("__main__"):
    csv_path = None # CSV PATH

    folder_path = "../data/"
    folder = folder_path + "v1/"
    average_reward_graph("../q-bet-agent/PPO_logs/cs2/PPO_cs2_log_5.csv")
    '''
    winners = build_match_winner_lookup(folder)

    with open(folder_path + "winners/match_winners.json", "w", encoding="utf-8") as out:
        json.dump(winners, out, indent=2)
    print("Built lookup for", len(winners), "matches")
    '''
