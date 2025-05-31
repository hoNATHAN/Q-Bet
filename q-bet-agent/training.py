import json
import random
from ppo import Agent
from agent_utils import load_data, winners_path

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
        return 10.0

    # if we bet and lose, we lose our stake => −1
    return -1.0


def training():
    batch_states = load_data()

    N_ACTIONS = 3  # 0 = bet A, 1 = bet B, 2 = abstain
    INPUT_DIMS = (19,)
    BATCH_SIZE = 64
    N_EPOCHS = 1
    ALPHA = 3e-4

    agent = Agent(
        n_actions=N_ACTIONS,
        input_dims=INPUT_DIMS,
        batch_size=BATCH_SIZE,
        alpha=ALPHA,
        n_epochs=N_EPOCHS,
    )

    for epoch in range(1, N_EPOCHS + 1):
        random.shuffle(batch_states)
        for game_states in batch_states:
            if game_states is None:
                print("game_state null")
                continue
            for idx, (match_id, game_idx, state) in enumerate(game_states):
                # consider keeping stuff on CUDA GPU
                # state = state.to(agent.device)

                action, logp, value = agent.choose_action(state)
                winner = lookup_winner(match_id, game_idx)
                reward = compute_reward(int(action), winner)

                # allow multi step episodes
                done = idx == len(game_states) - 1
                agent.remember(state, action, logp, value, reward, done)
                # print(action, match_id, game_idx)

                if done or len(agent.memory.states) >= BATCH_SIZE:
                    agent.learn()

            # agent.save_models()
        print(f"=== Epoch {epoch}/{N_EPOCHS} complete ===")


if __name__ == "__main__":
    training()
