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

os.makedirs("graphs", exist_ok=True)

def cumulative_reward_graph():
    """
    Creates a graph that shows Normalized Cumulative Rewards over time for multiple agents.
    """
    # Map descriptive labels to file paths
    training_csv_files = {
        "Binary Basic (Crafted)": "../q-bet-agent/logs/binary_basic_crafted/step_log.csv",
        "Binary Basic (Raw)": "../q-bet-agent/logs/binary_basic_raw/step_log.csv",
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/step_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/step_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/step_log.csv",
    }

    plt.figure(figsize=(12, 7))

    for label, path in training_csv_files.items():
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue

        df = pd.read_csv(path)
        rewards = df["cumulative_reward"]
        normalized = (rewards - rewards.mean()) / rewards.std()
        plt.plot(df["time_step"], normalized, label=label)

    plt.title("Normalized Cumulative Reward vs. Time Step (All Agents) Training")
    plt.xlabel("Time Step")
    plt.ylabel("Normalized Cumulative Reward")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/cumulative_reward_all_training.pdf", bbox_inches="tight")
    plt.close()

    testing_csv_files = {
        "Binary Basic (Crafted)": "../q-bet-agent/logs/binary_basic_crafted/test_log.csv",
        "Binary Basic (Raw)": "../q-bet-agent/logs/binary_basic_raw/test_log.csv",
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/test_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/test_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/test_log.csv",
    }

    plt.figure(figsize=(12, 7))

    for label, path in testing_csv_files.items():
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue

        df = pd.read_csv(path)
        rewards = df["cumulative_reward"]
        normalized = (rewards - rewards.mean()) / rewards.std()
        plt.plot(df["episode"], normalized, label=label)

    plt.title("Normalized Cumulative Reward vs. Episode (All Agents) Testing")
    plt.xlabel("Episode")
    plt.ylabel("Normalized Cumulative Reward")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/cumulative_reward_all_testing.pdf", bbox_inches="tight")
    plt.close()

def policy_value_loss_graph(csv_file, agent_type):
    """
    Creates a graph that shows Policy and Value Loss over time

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["time_step", "return_mean", "return_std", "policy_loss", "value_loss"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    plt.figure(figsize=(10,6))
    plt.plot(csv_df["episode"], csv_df["policy_loss"], label="Policy Loss")
    plt.plot(csv_df["episode"], csv_df["value_loss"], label="Value Loss")
    plt.title(f"Policy and Value Loss vs. Episode: Agent {agent_type}")
    plt.xlabel("Episode")
    plt.ylabel("Policy and Value Loss Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"graphs/policy_value_loss_{agent_type}.pdf", bbox_inches="tight")
    plt.close()

def return_distribution_graph(csv_file, agent_type):
    """
    Creates a graph that shows return distribution

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["episode", "final_balance", "cumulative_reward"]
        agent_type: String of agent type
    """
    csv_df = pd.read_csv(csv_file)

    plt.figure(figsize=(10,6))
    plt.hist(csv_df["cumulative_reward"], bins=30, edgecolor='black')
    plt.title(f"Return Distribution (per Episode): Agent {agent_type}")
    plt.xlabel("Cumulative Reward")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"graphs/return_distribution_{agent_type}.pdf", bbox_inches="tight")
    plt.close()

def bankroll_graph():
    """
    Creates a graph that shows bankroll over time (EPISODE)

    Parameters:
        csv_file: String of full path of csv file that has the rows: ["time_step", "episode", "reward", "cumulative_reward", "balance", "p_chosen", "correct"]
        agent_type: String of agent type
    """
    training_csv_files = {
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/step_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/step_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/step_log.csv",
    }

    plt.figure(figsize=(12, 7))

    for label, path in training_csv_files.items():
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue

        df = pd.read_csv(path)
        plt.plot(df["time_step"], df["balance"], label=label)

    plt.title("Bankroll Over Time (All Agents) Training")
    plt.xlabel("Time Step")
    plt.ylabel("Balance")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/bankroll_all_training.pdf", bbox_inches="tight")
    plt.close()

    testing_csv_files = {
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/test_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/test_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/test_log.csv",
    }

    plt.figure(figsize=(12, 7))

    for label, path in testing_csv_files.items():
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue

        df = pd.read_csv(path)
        plt.plot(df["episode"], df["balance"], label=label)

    plt.title("Bankroll Over Time (All Agents) Testing")
    plt.xlabel("Episode")
    plt.ylabel("Balance")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/bankroll_all_testing.pdf", bbox_inches="tight")
    plt.close()

def prob_calibration_graph():
    """
    Creates a probability calibration graph for multiple agents.
    Each agent's calibration curve is plotted on the same figure.
    """
    testing_csv_files = {
        "Binary Basic (Crafted)": "../q-bet-agent/logs/binary_basic_crafted/test_log.csv",
        "Binary Basic (Raw)": "../q-bet-agent/logs/binary_basic_raw/test_log.csv",
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/test_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/test_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/test_log.csv",
    }

    plt.figure(figsize=(10, 6))

    for label, path in testing_csv_files.items():
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue

        csv_df = pd.read_csv(path)

        # Ensure required columns are present
        if "p_chosen" not in csv_df.columns or "correct" not in csv_df.columns:
            print(f"Missing required columns in: {path}")
            continue

        y_true = csv_df["correct"]
        y_prob = csv_df["p_chosen"]

        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy='uniform')

        plt.plot(prob_pred, prob_true, marker='o', label=label)

    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')
    plt.title("Probability Calibration Plot")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Empirical Accuracy")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("graphs/probability_distribution_all.pdf", bbox_inches="tight")
    plt.close()

if __name__ == ("__main__"):
    # define update logs for policy/value loss
    update_csv_files = {
        "Binary Basic (Crafted)": "../q-bet-agent/logs/binary_basic_crafted/update_log.csv",
        "Binary Basic (Raw)": "../q-bet-agent/logs/binary_basic_raw/update_log.csv",
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/update_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/update_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/update_log.csv",
    }
    testing_csv_files = {
        "Binary Basic (Crafted)": "../q-bet-agent/logs/binary_basic_crafted/test_log.csv",
        "Binary Basic (Raw)": "../q-bet-agent/logs/binary_basic_raw/test_log.csv",
        "Complex Discrete (Crafted)": "../q-bet-agent/logs/complex_complex_discrete_crafted/test_log.csv",
        "Complex Discrete (Raw)": "../q-bet-agent/logs/complex_complex_discrete_raw/test_log.csv",
        "Complex Continuous (Crafted)": "../q-bet-agent/logs/complex_complex_continuous_crafted/test_log.csv",
    }
    cumulative_reward_graph()

    for label, path in update_csv_files.items():
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue
        policy_value_loss_graph(path, label)
    
    for label, path in testing_csv_files.items():
        if not os.path.exists(path):
            print(f"[Warning] File not found: {path}")
            continue

        print(path)
        return_distribution_graph(path, label)

    bankroll_graph()
    prob_calibration_graph()
        
    '''
    parser = argparse.ArgumentParser(description="Generate graphs from agent logs.")
    parser.add_argument("--csv_path", type=str, help="Path to the CSV files")
    parser.add_argument("--agent_type", type=str, help="Type/name of the agent")

    args = parser.parse_args()

    csv_path = args.csv_path
    agent_type = args.agent_type

    csv_files = [f for f in os.listdir(csv_path) if os.path.isfile(os.path.join(csv_path, f))]
    step_log_file = next((os.path.join(csv_path, f) for f in csv_files if "step_log" in f), None)
    update_log_file = next((os.path.join(csv_path, f) for f in csv_files if "update_log" in f), None)
    episode_log_file = next((os.path.join(csv_path, f) for f in csv_files if "episode_log" in f), None)

    cumulative_reward_graph(step_log_file, agent_type)
    policy_value_loss_graph(update_log_file, agent_type)
    return_distribution_graph(episode_log_file, agent_type)
    bankroll_graph(step_log_file, agent_type)
    prob_calibration_graph(step_log_file, agent_type)
    '''
