import os
import json

from ppo_mc import PPO
from datetime import datetime

from agent_utils import load_data, winners_path
from sklearn.model_selection import train_test_split

_WINNER_LOOKUP = None


def _load_winner_lookup(path=winners_path):
    """
    Will search winner based on path
    """
    global _WINNER_LOOKUP
    if _WINNER_LOOKUP is None:
        with open(path, "r", encoding="utf-8") as f:
            _WINNER_LOOKUP = json.load(f)
    return _WINNER_LOOKUP


def lookup_winner(match_id: str, game_idx: int) -> int:
    """
    Given a match_id (e.g. "3dmax-vs-gamerlegion-21-04-2025")
    and a 1-based game index (1,2,3,...),
    returns 0 if Team A won, 1 if Team B won.
    Raises KeyError if data is missing.
    """
    lookup = _load_winner_lookup()
    match_info = lookup.get(match_id)
    if match_info is None:
        raise KeyError(f"No entry for match_id={match_id}")

    key = f"game{game_idx + 1}"
    winner = match_info.get(key)
    if winner is None:
        raise KeyError(f"No winner recorded for {match_id} {key}")

    w = winner.strip().lower()
    if w == "team a":
        return 0
    elif w == "team b":
        return 1
    else:
        raise ValueError(f"Unrecognized winner '{winner}' for {match_id} {key}")


# include roi in reward ?
def compute_reward(action: int, winner_idx: int) -> float:
    """
    action:      0 = bet Team A, 1 = bet Team B, 2 = abstain
    winner_idx:  0 if Team A actually won, 1 if Team B actually won
    roi:         (decimal_odds − 1) / decimal_odds  for the CORRECT side

    returns a scalar reward for this one bet.
    """
    # iff we abstained, no gain or loss
    if action == 2:
        return 0.0

    # if we bet on the right team, reward = market ROI
    if action == winner_idx:
        return 1.0

    # if we bet and lose, we lose our stake => −1
    return -1.0


def training(batch_states):
    agent = PPO(
        state_dim=19,
        action_dim=3,
        lr_actor=0.0003,
        lr_critic=0.001,
        gamma=0.99,
        K_epochs=80,
        eps_clip=0.2,
        has_continuous_action_space=False,
        action_std_init=0.6,
    )

    # ----------------------------
    # hyperparams
    # ----------------------------
    max_ep_len = 10  # max timesteps taken in one episode
    max_training_timesteps = int(
        3e6
    )  # break training if timesteps > max_training_timesteps
    print_freq = max_ep_len * 10  # print average reward in interval
    log_freq = max_ep_len * 2  # log average reward in the interval
    save_model_freq = int(1e5)  # save model frequency

    # ----------------------------
    # variables to track
    # ----------------------------
    time_step = 0  # total environment steps so far
    running_reward = 0.0  # sum of rewards in the last print interval
    episode_length = 0  # length of current episode in timesteps
    completed_episodes = 0
    avg_length = 0  # total lengths of all finished episodes (for averaging)
    update_timestep = max_ep_len * 4  # update policy every n timesteps

    directory = "PPO_preTrained"
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = directory + "/" + "cs2" + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    checkpoint_path = directory + "PPO_{}_{}.pth".format("cs2", time_step)
    print("save checkpoint path : " + checkpoint_path)

    # logging file
    #### log files for multiple runs are NOT overwritten
    log_dir = "PPO_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_dir = log_dir + "/" + "cs2" + "/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    run_num = 0
    current_num_files = next(os.walk(log_dir))[2]
    run_num = len(current_num_files)
    log_f_name = log_dir + "/PPO_" + "cs2" + "_log_" + str(run_num) + ".csv"
    log_f = open(log_f_name, "w+")
    log_f.write("episode,timestep,reward\n")

    log_running_reward = 0
    log_running_episodes = 0

    # TRAINING
    i_episode = 0
    print_running_reward = 0
    print_running_episodes = 0
    start_time = datetime.now().replace(microsecond=0)
    while time_step <= max_training_timesteps:
        for game_states in batch_states:
            # break if training limit hit
            if time_step > max_training_timesteps:
                break

            # break if game state is not found
            if game_states is None:
                print("game_state null")
                continue

            episode_length = 0
            completed_episodes += 1
            current_ep_reward = 0

            done = False

            for idx, (match_id, game_idx, state) in enumerate(game_states):
                if state.numel() == 0:
                    print("empty tensor found for", match_id, game_idx)
                    break

                action = agent.select_action(state)
                winner = lookup_winner(match_id, game_idx)
                reward = compute_reward(int(action), winner)

                agent.buffer.rewards.append(reward)
                agent.buffer.is_terminals.append(done)

                running_reward += reward
                current_ep_reward += reward
                print_running_reward += reward
                log_running_reward += reward

                done = idx == len(game_states) - 1

                time_step += 1
                episode_length += 1

                if time_step % update_timestep == 0:
                    agent.update()

                # log in logging file
                if time_step % log_freq == 0:
                    # log average reward till last episode
                    log_avg_reward = log_running_reward / (log_running_episodes + 1e-6)
                    log_avg_reward = round(log_avg_reward, 4)

                    log_f.write(
                        "{},{},{}\n".format(i_episode, time_step, log_avg_reward)
                    )
                    log_f.flush()

                    log_running_reward = 0
                    log_running_episodes = 0

                # printing average reward
                if time_step % print_freq == 0:
                    # print average reward till last episode
                    print_avg_reward = print_running_reward / (
                        print_running_episodes + 1e-6
                    )
                    print_avg_reward = round(print_avg_reward, 2)

                    print(
                        "Episode : {} \t\t Timestep : {} \t\t Average Reward : {}".format(
                            i_episode, time_step, print_avg_reward
                        )
                    )

                    print_running_reward = 0
                    print_running_episodes = 0

                # save model weights
                if time_step % save_model_freq == 0:
                    print(
                        "--------------------------------------------------------------------------------------------"
                    )
                    print("saving model at : " + checkpoint_path)
                    agent.save(checkpoint_path)
                    print("model saved")
                    print(
                        "Elapsed Time  : ",
                        datetime.now().replace(microsecond=0) - start_time,
                    )
                    print(
                        "--------------------------------------------------------------------------------------------"
                    )

                if done:
                    break

            print_running_reward += current_ep_reward
            print_running_episodes += 1

            log_running_reward += current_ep_reward
            log_running_episodes += 1

            avg_length += episode_length

            i_episode += 1

    log_f.close()

    # print total training time
    print(
        "============================================================================================"
    )
    end_time = datetime.now().replace(microsecond=0)
    print("Started training at (GMT) : ", start_time)
    print("Finished training at (GMT) : ", end_time)
    print("Total training time  : ", end_time - start_time)
    print(f"Total timesteps: {time_step}.")
    if completed_episodes > 0:
        print(f"Total episodes completed: {completed_episodes}.")
        print(
            f"Average episode length: {avg_length / completed_episodes:.2f} timesteps."
        )
    print(
        "============================================================================================"
    )


def testing(test_states):
    print(
        "============================================================================================"
    )
    agent = PPO(
        state_dim=19,
        action_dim=3,
        lr_actor=0.0003,
        lr_critic=0.001,
        gamma=0.99,
        K_epochs=80,
        eps_clip=0.2,
        has_continuous_action_space=False,
        action_std_init=0.6,
    )
    total_test_episodes = len(test_states)
    run_num_pretrained = 0  #### set this to load a particular checkpoint num

    # ----------------------------
    # hyperparams
    # ----------------------------
    max_ep_len = 1  # max timesteps taken in one episode

    directory = "PPO_preTrained" + "/" + "cs2" + "/"
    checkpoint_path = directory + "PPO_{}_{}.pth".format("cs2", run_num_pretrained)
    print("loading network from : " + checkpoint_path)

    agent.load(checkpoint_path)

    print(
        "--------------------------------------------------------------------------------------------"
    )
    test_running_reward = 0


if __name__ == "__main__":
    all_states = load_data()
    # 80% train / 20% test
    train_states, test_states = train_test_split(
        all_states,
        test_size=0.2,
        random_state=42,
        shuffle=True,
    )

    training(train_states)
    testing(test_states)
