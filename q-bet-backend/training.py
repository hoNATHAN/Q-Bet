from ppo import PPOAgent
from feature_vector import process_state
import random
from action_space import BET_PERCENTAGES

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


def train_agent(episodes, balance=1000):
    # Initialize agent with input size matching your feature vector
    input_size = 28  # Adjust based on your actual feature vector size
    agent = PPOAgent(input_size)

    for episode in range(1, episodes + 1):
        # Get initial game state (you would replace this with your actual state processing)
        state = process_state(sample_state_json)  # This should return a numpy array

        done = False
        score = 0
        current_balance = balance

        while not done:
            # Agent chooses action
            action, prob, val = agent.choose_action(state)
            bet_percentage = BET_PERCENTAGES[action]
            bet_amount = current_balance * bet_percentage

            # Simulate bet outcome (in a real scenario, this would come from actual match results)
            # For training, we'll use a simple win/loss simulation
            # Team A has 60% chance to win based on their economy advantage
            team_a_econ = state[0]  # Assuming first feature is team A economy
            win_probability = 0.5 + 0.5 * (
                team_a_econ - 0.5
            )  # Simple probability based on economy

            # Determine if bet wins (in reality, this would come from actual match outcome)
            if random.random() < win_probability:
                # Bet wins - double the bet amount
                reward = bet_amount
                current_balance += bet_amount
            else:
                # Bet loses - lose the bet amount
                reward = -bet_amount
                current_balance -= bet_amount

            # Store transition in memory
            agent.memory.store_memory(state, action, prob, val, reward, done)

            # Get next state (in a real scenario, this would be the next round or match state)
            # For training, we'll just use the same state for simplicity
            next_state = state

            # Update state
            state = next_state
            score += reward

            # If balance goes to zero, episode ends
            if current_balance <= 0:
                done = True

        # Learn from the episode
        agent.learn()

        print(
            f"Episode {episode}, Score: {score:.2f}, Final Balance: {current_balance:.2f}"
        )

    # Save trained models
    agent.save_models("models")


if __name__ == "__main__":
    # Initialize agent
    input_size = 41  # Must match your feature vector size
    agent = PPOAgent(input_size)

    # Process game state
    state_tensor = process_state(sample_state_json)
    state = state_tensor.numpy()  # Convert to numpy array

    # Get agent's betting decision
    action, _, _ = agent.choose_action(state)

    try:
        bet_percentage = BET_PERCENTAGES[action]
        print(f"Selected action: {action}")
        print(f"Agent recommends betting {bet_percentage * 100:.0f}% of balance")
    except KeyError:
        print(f"Error: Invalid action index {action}. Valid actions are 0-6.")
