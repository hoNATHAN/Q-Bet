# main_ppo.py

import os
import csv
import sys
import random
import argparse

import torch
import numpy as np
from sklearn.model_selection import train_test_split

from q_bet_env    import QBetEnv
from ppo_mc       import PPO
from agent_utils  import load_data

def main():
    #parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Train PPO agent with configurable rewards and action space"
    )
    parser.add_argument(
        '--reward-scheme', choices=['basic', 'binary', 'complex'], default='basic',
        help='Reward scheme: basic (odds-based net profit), binary (+1 for correct/-1 for incorrect/0 for abstain), or complex (ROI based)'
    )
    parser.add_argument(
        '--action-space', choices=['basic', 'complex_discrete', 'complex_continuous'], default='basic',
        help='Action space: basic, complex_discrete (fixed fractions), or complex_continuous (any fraction in [0,1])'
    )
    parser.add_argument(
        '--resume', action='store_true',
        help='If set, load the latest checkpoint from the per-config model directory before training'
    )
    parser.add_argument(
        '--initial-balance', type=float, default=1000.0,
        help='Initial bankroll balance to start with'
    )
    parser.add_argument(
        '--feature-type', choices=['crafted', 'raw'], default='crafted',
        help='Feature vector type: crafted (engineered) or raw (full raw features)'
    )
    args = parser.parse_args()
    #states which options were selected
    print(f"Using reward scheme: {args.reward_scheme}, action space: {args.action_space}, feature type: {args.feature_type}")
    # make per-config model and log dirs
    model_dir = f"models/{args.reward_scheme}_{args.action_space}_{args.feature_type}"
    os.makedirs(model_dir, exist_ok=True)
    log_dir = f"logs/{args.reward_scheme}_{args.action_space}_{args.feature_type}"
    os.makedirs(log_dir, exist_ok=True)

    #selects cuda if its present
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # select feature vector and load match-level data
    use_raw = (args.feature_type == 'raw')
    all_matches = load_data(raw=use_raw)   # now returns List[List[(mid,game_idx,feat)]]
    train_states, test_states = train_test_split(
        all_matches, test_size=0.2, random_state=42, shuffle=True
    )

    #builds the environment with the selected states and action space
    env = QBetEnv(
        states=train_states,
        reward_scheme=args.reward_scheme,
        action_space_type=args.action_space,
        initial_balance=args.initial_balance
    )
    print(f"Environment initialized with {len(train_states)} training states and {len(test_states)} test states.")


    #selects the appropriate action space and state dimensions
    state_dim = env.observation_space.shape[0]
    if args.action_space == 'complex_continuous':
        action_dim = env.action_space.shape[0]   #two floats
        is_continuous = True
    elif args.action_space == 'complex_discrete':
        #multiDiscrete([3, N]) → action_dim = 3 + N for PPO’s two-head setup
        N = len(env.discrete_stakes)
        action_dim = 3 + N
        is_continuous = False
    else:  #basic
        action_dim = env.action_space.n         # = 3
        is_continuous = False

    #initializes the PPO agent with the specified parameters
    agent = PPO(
        state_dim,
        action_dim,
        lr_actor=0.0003,
        lr_critic=0.001,
        gamma=0.99,
        K_epochs=80,
        eps_clip=0.2,
        has_continuous_action_space=is_continuous,
        action_std_init=0.6,
        device=device
    )

    #optionally resume from latest checkpoint
    agent.policy_old.to(device)
    agent.policy.to(device)
    if args.resume:
        resume_path = os.path.join(model_dir, 'ppo_latest.pth')
        if os.path.isfile(resume_path):
            agent.load(resume_path)
            print(f"Resuming training from checkpoint: {resume_path}")
        else:
            print(f"No checkpoint found at {resume_path}, starting fresh.")


    #we log each step: time_step, episode, reward, cumulative_reward, balance, stake_a, stake_b, p_chosen, correct
    stepF = open(f"{log_dir}/step_log.csv", "w", newline="")
    stepW = csv.writer(stepF)
    stepW.writerow([
        "time_step", "episode", "reward", "cumulative_reward",
        "balance", "stake_a", "stake_b", "p_chosen", "correct"
    ])

    #we log each update: episode, return_mean, return_std, policy_loss, value_loss, entropy
    updF = open(f"{log_dir}/update_log.csv", "w", newline="")
    updW = csv.writer(updF)
    updW.writerow([
        "episode", "return_mean", "return_std",
        "policy_loss", "value_loss", "entropy"
    ])

    #we log each episode: episode, final_balance, cum_reward
    epiF = open(f"{log_dir}/episode_log.csv", "w", newline="")
    epiW = csv.writer(epiF)
    epiW.writerow(["episode", "final_balance", "cum_reward"])

    #get all of the training states and shuffle them 
    match_indices = list(range(len(train_states)))
    random.shuffle(match_indices)

    #establish the number of episodes, the save frequency, and the time step that we start at 
    n_episodes   = 7000
    save_freq    = 1000
    time_step    = 0

    #for each episode, we select a match, reset the environment, and run the agent
    for ep in range(1, n_episodes + 1):
        if not match_indices: #if we run out of matches, we shuffle the indicies again 
            match_indices = list(range(len(train_states)))
            random.shuffle(match_indices)
        match_id = match_indices.pop()

        #reset the environment for the selected match
        obs = env.reset(match_idx=match_id) 
        done = False
        ep_reward = 0.0

        #for each step (round) in the match, we select an action, step the environment, and log the results 
        while not done:
            action = agent.select_action(obs)

            lp_tensor = agent.buffer.logprobs[-1] if agent.buffer.logprobs else None
            p_chosen = float(torch.exp(lp_tensor).cpu()) if lp_tensor is not None else 0.0

            obs, reward, done, info = env.step(action)

            #clip reward to +-1000 so that this does not explode
            reward = float(np.clip(reward, -1000.0, +1000.0))

            agent.buffer.rewards.append(reward)
            agent.buffer.is_terminals.append(done)

            time_step += 1
            ep_reward += reward
            balance = info.get('balance', 0.0)
            correct = 1 if reward > 0 else 0

            stake_a = info.get('stake_a', 0.0)
            stake_b = info.get('stake_b', 0.0)
            stepW.writerow([
                time_step, ep, f"{reward:.2f}", f"{ep_reward:.2f}",
                f"{balance:.2f}", f"{stake_a:.2f}", f"{stake_b:.2f}",
                f"{p_chosen:.2f}", correct
            ])

            if time_step % save_freq == 0:
                ckpt = f"{model_dir}/ppo_{time_step}.pth"
                agent.save(ckpt)
                print(f"Model saved at {ckpt}")

        final_balance = info.get('balance', 0.0)
        epiW.writerow([ep, f"{final_balance:.2f}", f"{ep_reward:.2f}"])

        if ep % 50 == 0:
            agent.update()
            print(f"[Episode {ep}] Policy updated after {ep} matches")
            metrics = agent.last_update_metrics
            updW.writerow([
                ep,
                f"{metrics['return_mean']:.2f}",
                f"{metrics['return_std']:.2f}",
                f"{metrics['policy_loss']:.4f}",
                f"{metrics['value_loss']:.4f}",
                f"{metrics['entropy']:.4f}"
            ])

        if ep % 10 == 0:
            print(f"[Episode {ep}/{n_episodes}]  Reward: {ep_reward:.2f}  Balance: {final_balance:.2f}")

    if len(agent.buffer.rewards) > 0:
        agent.update()
        print("Final PPO update on leftover episodes")

    agent.save("models/ppo_latest.pth")
    print("Training done")
    # save final model per config
    agent.save(f"{model_dir}/ppo_latest.pth")
    
    # run testing and log results
    testing(agent, test_states, device, args.reward_scheme, args.action_space, args.initial_balance, log_dir)

    print("\n=== Baseline Random Agent Testing ===")
    random_agent_test(test_states, device, log_dir)


def testing(agent, test_states, device, reward_scheme, action_space_type, initial_balance, log_dir):
    """
    Runs the trained `agent` on each match in `test_states`,
    prints per-episode reward+balance, and overall average reward.
    """
    # open test log file
    testF = open(f"{log_dir}/test_log.csv", "w", newline="")
    testW = csv.writer(testF)
    testW.writerow(["episode", "reward", "cumulative_reward", "balance", "p_chosen", "correct", "status"])
    print("\n" + "="*60)
    print("BEGIN TESTING")

    test_env = QBetEnv(
        states=test_states,
        reward_scheme=reward_scheme,
        action_space_type=action_space_type,
        initial_balance=initial_balance
    )
    agent.policy_old.to(device)
    total_reward = 0.0
    total_balance = 0.0

    for ep, _ in enumerate(test_states, start=1):
        obs = test_env.reset()
        done = False
        ep_reward = 0.0

        while not done:
            with torch.no_grad():
                    action = agent.select_action(obs)
        
            obs, reward, done, info = test_env.step(action)
            ep_reward += reward
            total_balance += info.get('balance', 0.0)

        # successful completion
        total_reward += ep_reward
        total_balance += info.get('balance', 0.0)
        print(f"[Test Ep {ep:3d}] Reward: {ep_reward:7.2f}  Balance: {info['balance']:7.2f}")
        # compute action probability and correctness
        lp_tensor = agent.buffer.logprobs[-1] if agent.buffer.logprobs else None
        p_chosen = float(torch.exp(lp_tensor).cpu()) if lp_tensor is not None else 0.0
        correct = 1 if ep_reward > 0 else 0
        testW.writerow([ep, f"{ep_reward:.2f}", f"{total_reward:.2f}", f"{info.get('balance', 0.0):.2f}", f"{p_chosen:.2f}", correct, 'success'])
        agent.buffer.clear()

    avg_reward = total_reward / max(len(test_states), 1)
    avg_balance = total_balance / max(len(test_states), 1)
    print(f"\nAverage Test Reward over {len(test_states)} episodes: {avg_reward:.2f}")
    testW.writerow(['average', f"{avg_reward:.2f}", '', f"{avg_balance:.2f}", '', '', ''])
    testF.close()
    print("END TESTING")


def random_agent_test(test_states, device, log_dir):
    """
    Tests a random agent that selects actions uniformly for baseline comparison.
    """
    # open random baseline log file
    randomF = open(f"{log_dir}/random_log.csv", "w", newline="")
    randomW = csv.writer(randomF)
    randomW.writerow(["episode", "reward", "balance"])
    print("\n" + "="*60)
    print("BEGIN RANDOM BASELINE TESTING")

    test_env = QBetEnv(states=test_states)
    total_reward = 0.0
    total_balance = 0.0

    for ep in range(1, len(test_states) + 1):
        obs = test_env.reset()
        done = False
        ep_reward = 0.0

        while not done:
            action = random.randint(0, 2)
            obs, reward, done, info = test_env.step(action)
            ep_reward += reward

        total_reward += ep_reward
        total_balance += info.get('balance', 0.0)
        print(f"[Random Ep {ep:3d}] Reward: {ep_reward:7.2f}  Balance: {info.get('balance'):7.2f}")
        randomW.writerow([ep, f"{ep_reward:.2f}", f"{info.get('balance', 0.0):.2f}"])

    avg_reward = total_reward / max(len(test_states), 1)
    avg_balance = total_balance / max(len(test_states), 1)
    print(f"\nAverage Random Reward over {len(test_states)} episodes: {avg_reward:.2f}")
    print(f"Average Random Final Balance: {avg_balance:.2f}")
    randomW.writerow(['average', f"{avg_reward:.2f}", f"{avg_balance:.2f}"])
    randomF.close()
    print("END RANDOM BASELINE TESTING")


if __name__ == "__main__":
    main()
