"""
File: generate_graph.py
Author: Matt Protacio
Date: 2025-06-01
Description:
    Takes a csv file and generates graphs based on the columns
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
import argparse

def cumulative_reward_graph(csv_file, agent_type):
    """
    Creates a graph that shows Cumulative Rewards over time

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["time_step", "episode", "reward", "cumulative_reward", "balance", "p_chosen", "correct"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    # Uncomment this if csv is printed every time_step
    #cum_rewards = csv_df.groupby("episode")["reward"].mean().reset_index()
    #time_type = "Episodes"
    #plt.plot(cum_rewards["episode"], cum_rewards["average_reward"], marker='o')

    # Uncomment this if csv is printed every timestep
    #time_type = "Time Step"
    #plt.plot(cum_rewards["time_step"], cum_rewards["average_reward"], marker='o')

    plt.figure(figsize=(10,6))
    plt.title(f"Cumulative Reward vs. {time_type}: Agent {agent_type}")
    plt.xlabel(time_type)
    plt.ylabel("Cumulative Reward")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def policy_value_loss_graph(csv_file, agent_type):
    """
    Creates a graph that shows Policy and Value Loss over time

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["time_step", "return_mean", "return_std", "policy_loss", "value_loss"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    plt.figure(figsize=(10,6))
    plt.plot(csv_df["time_step"], csv_df["policy_loss"], label="Policy Loss")
    plt.plot(csv_df["time_step"], csv_df["value_loss"], label="Value Loss")
    plt.title(f"Cumulative Reward vs. Time Step: Agent {agent_type}")
    plt.xlabel("Time Step")
    plt.ylabel("Policy and Value Loss Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def return_distribution_graph(csv_file, agent_type):
    """
    Creates a graph that shows return distribution

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["episode", "final_balance", "cumulative_reward"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    plt.figure(figsize=(10,6))
    plt.plot(csv_df["cumulative_reward"], bins=30, edgecolor='black')
    plt.title(f"Return Distribution (per Episode): Agent {agent_type}")
    plt.xlabel("Cumulative Reward")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def bankroll_graph(csv_file, agent_type):
    """
    Creates a graph that shows bankroll over time

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["time_step", "episode", "reward", "cumulative_reward", "balance", "p_chosen", "correct"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    plt.figure(figsize=(10,6))
    plt.plot(csv_df["time_step"], csv_df["balance"])
    plt.title(f"Bankroll Over Time: Agent {agent_type}")
    plt.xlabel("Time Step")
    plt.ylabel("Balance")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def prob_calibration_graph(csv_file, agent_type):
    """
    Creates a probability calibration graph

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["time_step", "episode", "reward", "cumulative_reward", "balance", "p_chosen", "correct"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    y_true = csv_df["correct"]
    y_prob = csv_df["p_chosen"]

    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy='uniform')

    plt.figure(figsize=(10,6))
    plt.plot(prob_pred, prob_true, marker='o', label='Agent Calibration')
    plt.plot([0, 1], [0, 1], linestyle='--', label='Perfect Calibration')
    plt.title(f"Probability Calibration Plot: Agent {agent_type}")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Empirical Accuracy")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == ("__main__"):
    arser = argparse.ArgumentParser(description="Generate graphs from agent logs.")
    parser.add_argument("--csv_file", type=str, help="Path to the CSV file")
    parser.add_argument("--agent_type", type=str, help="Type/name of the agent")

    args = parser.parse_args()

    csv_file = args.csv_file
    agent_type = args.agent_type
    csv_path = None # CSV PATH

    # Add Processing to get csvs relavent to agent?

    cumulative_reward_graph(csv_file, agent_type)
    policy_value_loss_graph(csv_file, agent_type)
    return_distribution_graph(csv_file, agent_type)
    bankroll_graph(csv_file, agent_type)
    prob_calibration_graph(csv_file, agent_type)
