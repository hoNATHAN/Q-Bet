import os, csv
import sys
import torch
from q_bet_env import QBetEnv
from ppo_mc import PPO
from agent_utils import load_data
from sklearn.model_selection import train_test_split

def main():


    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")


    all_states = load_data()

    train_states, test_states = train_test_split(all_states, test_size=0.2, random_state=42, shuffle=True)


    env = QBetEnv(states=train_states)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    agent = PPO(
        state_dim,
        action_dim,
        lr_actor=0.0003,
        lr_critic=0.001,
        gamma=0.99,
        K_epochs=80,
        eps_clip=0.2,
        has_continuous_action_space=False,
        action_std_init=0.6,
        device=device
    )

    agent.policy_old.to(device)
    agent.policy.to(device)

    os.makedirs('models', exist_ok=True)
    os.makedirs("PPO_LOGS", exist_ok=True)
    log_path = os.path.join("PPO_LOGS", "train_log.csv")
    log_fh = open(log_path, "w", newline="")
    logger = csv.writer(log_fh)
    logger.writerow(["Episode","TimeStamp", "Reward", "RunningAverage"])

    n_episodes = 1000
    update_timestep = 1000
    log_freq = 1000
    save_freq = 1000
    time_step = 0
    running_reward = 0.0
    running_episodes = 0

    for ep in range(1, n_episodes + 1):
        obs = env.reset()
        done = False
        ep_reward = 0.0

        while not done:
            action = agent.select_action(obs)
            obs, reward, done, info = env.step(action)

            agent.buffer.rewards.append(reward)
            agent.buffer.is_terminals.append(done)
            
            time_step += 1
            ep_reward += reward
            running_reward += reward

            if time_step % update_timestep == 0 and agent.buffer.states:
                agent.update()

            if time_step % log_freq == 0:
                avg_reward = running_reward / running_episodes if running_episodes > 0 else 0.0
                logger.writerow([ep, time_step, round(ep_reward, 2), round(avg_reward, 2)])
                log_fh.flush()

            if time_step % save_freq == 0:
                ckpt = f"models/ppo_{time_step}.pth"
                agent.save(ckpt)
                print(f"[Saved checkpoint at {time_step} steps]")

        if agent.buffer.states:
            agent.update()
        running_episodes += 1

        if ep % 10 == 0:
            print(f"[Episode {ep}/{n_episodes}]  Reward: {ep_reward:.2f}  Balance: {info.get('balance',0):.2f}")

    agent.save("models/ppo_final.pth")
    log_fh.close()
    print("Training complete. Model saved.")


if __name__ == "__main__":
    main()
