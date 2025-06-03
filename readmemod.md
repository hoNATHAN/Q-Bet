# Q-Bet

**Final Project for CS 486 @ Drexel University**  
A reinforcement-learning–based betting agent for Counter-Strike 2 esports matches, implemented using Proximal Policy Optimization (PPO). Q-Bet ingests round-level JSON game data, computes both raw and crafted feature vectors (including market-signal features like Expected Value and Kelly Criterion), and trains discrete-action-space PPO agents under different reward-function formulations. The goal is to learn when to bet (and how much) to maximize overall bankroll growth.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Directory Structure](#directory-structure)
4. [Data Preparation](#data-preparation)
   - [Match JSON Files](#match-json-files)
   - [Winners Lookup](#winners-lookup)
5. [Usage](#usage)
   - [Configuring Hyperparameters](#configuring-hyperparameters)
   - [Training an Agent](#training-an-agent)
   - [Evaluating an Agent](#evaluating-an-agent)
   - [Visualizing Results](#visualizing-results)
6. [Feature Engineering](#feature-engineering)
   - [Raw Feature Vector](#raw-feature-vector)
   - [Crafted Feature Vector](#crafted-feature-vector)
7. [Reward Functions](#reward-functions)
   - [Basic Reward](#basic-reward)
   - [Complex Reward](#complex-reward)
8. [Action Spaces](#action-spaces)
   - [Basic Action Space](#basic-action-space)
   - [Complex Action Space](#complex-action-space)
9. [File/Module Descriptions](#filemodule-descriptions)
10. [Experiment Results](#experiment-results)
11. [Contributing](#contributing)
12. [License](#license)

---

## Project Overview

Q-Bet is a Python-based framework that trains on round-level Counter-Strike 2 match data to decide, at each round, whether to bet on Team A, bet on Team B, or abstain. Using PPO’s on-policy learning paradigm, the agent processes game-state snapshots (raw or crafted) and receives rewards based on betting outcomes. Two parallel reward formulations are implemented:

- **Basic reward**: +1 for correct pick, –1 for incorrect, 0 for abstain.
- **Complex reward**: Modeled on bankroll changes (incorporating bet‐sizing percentages and odds ROI).

The project compares agents using:

1. **Raw feature vectors**: Directly normalized game-state values.
2. **Crafted feature vectors**: Augmented with market signals such as implied probabilities, expected value (EV), Kelly Criterion metrics, and cost-per-kill (CPK).

By maintaining discrete action sets––either a small 3-action set (abstain, bet Team A, bet Team B) or a 9-action set (abstain plus betting {5 %, 10 %, 25 %, 50 %} of bankroll on either team)––agents can be trained and evaluated on simulated match sequences reflecting real-world betting constraints.

---

## Features

- **Proximal Policy Optimization (PPO)** implementation in PyTorch, with separate actor/critic networks.
- **Two feature representations**:
  - Raw (straight game-state tensor).
  - Crafted (engineered signals: EV, Kelly, implied probabilities, odds ROI, CPK).
- **Two reward functions**:
  - Basic (binary ±1/0).
  - Complex (bankroll dynamics using fractional stake and payout).
- **Discrete action spaces**:
  - Basic: 3 actions ‒ bet Team A, bet Team B, abstain.
  - Complex: 9 actions ‒ abstain + bet {5 %, 10 %, 25 %, 50 %} of current bankroll on either team.
- **JSON preprocessing pipeline**:
  - Efficient loading of match files.
  - Normalization and capping (e.g., round time, max econ values).
  - Multi-processing support to accelerate feature extraction.
- **Evaluation scripts**:
  - Bankroll-vs-round plots.
  - Cumulative reward distributions.
  - Probability calibration curves.
- **Configurable hyperparameters**:
  - Learning rates (`lr_actor`, `lr_critic`), discount (`gamma`), PPO clip (`eps_clip`), epochs (`K_epochs`), GAE lambda (`gae_lambda`), action-std, etc.
- **Visualization utilities**: Matplotlib hooks to generate plots for training vs. testing.

---

## Getting Started

### Prerequisites

- **Python 3.8 +**
- **PyTorch ≥ 1.9** (CPU or CUDA)
- **NumPy**
- **scikit-learn** (for any clustering or normalization routines)
- **Matplotlib** (for plotting)
- **tqdm** (optional, for progress bars)
- **pytest** (optional, for unit tests)

```bash
# Example (pip) dependencies
pip install torch numpy scikit-learn matplotlib tqdm pytest
```
