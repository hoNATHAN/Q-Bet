import torch
import os
from ppo import PPOAgent
from feature_vector import process_state
import random
from action_space import BET_PERCENTAGES
import numpy as np

sample_state_json = """
{
  "tournament": "PGL Astana 2025",
  "team_a": "FURIA",
  "team_b": "MIBR",
  "status": "Ended",
  "start_time": "May 12, 01:00",
  "link": "https://bo3.gg/matches/furia-vs-mibr-12-05-2025",
  "match_id": "furia-vs-mibr-12-05-2025",
  "game_count": 3,
  "game1": {
    "round_num": 17,
    "map": "train",
    "rounds": {
        "round_1": {
            "initial_team_a_econ": 4000,
            "initial_team_b_econ": 4000,
            "buy_team_a_econ": 600,
            "buy_team_b_econ": 600,
            "final_team_a_econ": 18400,
            "final_team_b_econ": 10600,
            "winner": "Team A",
            "win_type": "ace",
            "duration": 122,
            "team_a_buy_type": "Eco",
            "team_b_buy_type": "Eco",
            "score": "1-0",
            "players_alive_end": {
                "team_a": 0,
                "team_b": 0
            },
            "kills_end": {
                "team_a": 5,
                "team_b": 2
            },
            "assists_end": {
                "team_a": 0,
                "team_b": 0
            }
        }
    }
  }
}
"""

# test for single action
# if __name__ == "__main__":
#     # initialize agent
#     input_size = 41  # must match your feature vector size
#
#     # use to run on gpu
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#
#     agent = PPOAgent(input_size)
#
#     # process game state
#     state_tensor = process_state(sample_state_json)
#     state = state_tensor.numpy()  # convert to numpy array
#
#     # get agent's betting decision
#     action, _, _ = agent.choose_action(state)
#
#     start_time = time.time()
#     try:
#         bet_percentage = BET_PERCENTAGES[action]
#         print(f"Selected action: {action}")
#         print(f"Agent recommends betting {bet_percentage * 100:.0f}% of balance")
#     except KeyError:
#         print(f"Error: Invalid action index {action}. Valid actions are 0-6.")
#
#     print("--- Agent Performance: %s seconds ---" % (time.time() - start_time))


def train_agent(episodes, balance=1000):
    # Initialize agent with correct input size
    input_size = 41
    agent = PPOAgent(
        input_size,
        alpha=0.00005,  # Further reduced learning rate
        batch_size=32,  # Smaller batch size
        policy_clip=0.1,
        max_grad_norm=0.1,
        n_epochs=5,
    )  # Reduced number of epochs

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    agent.actor.to(device)
    agent.critic.to(device)

    # Create models directory
    os.makedirs("models", exist_ok=True)

    # Track metrics
    episode_rewards = []
    balance_history = []

    # Initialize state scaler
    state_means = None
    state_stds = None

    for episode in range(1, episodes + 1):
        try:
            state = process_state(sample_state_json)

            # Update running statistics for state normalization
            if state_means is None:
                state_means = state.mean(0)
                state_stds = state.std(0)
            else:
                state_means = 0.99 * state_means + 0.01 * state.mean(0)
                state_stds = 0.99 * state_stds + 0.01 * state.std(0)

            # Normalize state
            state = (state - state_means) / (state_stds + 1e-8)

            # Debug state values
            print(f"\nEpisode {episode} initial state stats:")
            print(f"State shape: {state.shape}")
            print(f"State mean: {state.mean().item():.4f}")
            print(f"State std: {state.std().item():.4f}")

            state = state.to(device)
            if len(state.shape) == 1:
                state = state.unsqueeze(0)

            done = False
            episode_reward = 0
            current_balance = balance
            step = 0
            max_steps = 50  # Reduced max steps

            while not done and step < max_steps:
                try:
                    # Debug actor output
                    with torch.no_grad():
                        probs = agent.actor(state)
                        if torch.isnan(probs).any():
                            print("NaN detected in action probabilities!")
                            break

                    action, prob, val = agent.choose_action(state)
                    bet_percentage = BET_PERCENTAGES[action]
                    bet_amount = current_balance * bet_percentage

                    # Calculate win probability based on normalized economy
                    team_a_econ = state[0][0].item()
                    win_probability = 0.5 + 0.05 * team_a_econ  # Further reduced impact

                    # Simulate outcome with smaller rewards
                    if random.random() < win_probability:
                        reward = bet_amount * 0.005  # Further reduced rewards
                        current_balance += bet_amount
                    else:
                        reward = -bet_amount * 0.005  # Further reduced rewards
                        current_balance -= bet_amount

                    # Clip reward to prevent extreme values
                    reward = np.clip(reward, -10, 10)

                    # Store the experience
                    agent.memory.store_memory(
                        state.cpu().numpy(),
                        action,
                        prob.item(),
                        val.item(),
                        reward,
                        done,
                    )

                    # Update state (in real scenario, this would be new game state)
                    next_state = state.clone()
                    state = next_state
                    episode_reward += reward
                    step += 1

                    if current_balance <= 0:
                        done = True
                        print(
                            f"Episode {episode}: Bankrupt! Final balance: {current_balance:.2f}"
                        )

                except Exception as e:
                    print(f"Error during episode {episode}, step {step}: {str(e)}")
                    break

            # Learn from experiences if we have enough samples
            if len(agent.memory.states) >= agent.memory.batch_size:
                try:
                    agent.learn()
                except Exception as e:
                    print(f"Error during learning in episode {episode}: {str(e)}")
                    agent.memory.clear_memory()  # Clear memory on error
                    continue

            episode_rewards.append(episode_reward)
            balance_history.append(current_balance)

            # Print progress every episode
            if episode % 1 == 0:
                avg_reward = sum(episode_rewards[-10:]) / min(10, len(episode_rewards))
                avg_balance = sum(balance_history[-10:]) / min(10, len(balance_history))
                print(f"\nEpisode {episode} Summary:")
                print(f"Average Reward (last 10): {avg_reward:.2f}")
                print(f"Average Balance (last 10): {avg_balance:.2f}")
                print(f"Current Balance: {current_balance:.2f}")

                # Save intermediate models
                if episode % 10 == 0:
                    agent.save_models("models")
                    print("Model checkpoint saved")

        except Exception as e:
            print(f"Fatal error in episode {episode}: {str(e)}")
            continue  # Continue to next episode instead of raising

    # Final save
    agent.save_models("models")
    print("Training completed! Final models saved")


if __name__ == "__main__":
    # Training configuration
    training_episodes = 100
    initial_balance = 1000

    print(f"Starting training for {training_episodes} episodes...")
    train_agent(episodes=training_episodes, balance=initial_balance)
    print("Training completed!")
