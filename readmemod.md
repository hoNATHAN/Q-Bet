# Q-Bet

**Final Project for CS 486 @ Drexel University**

A reinforcement-learning betting agent for Counter-Strike 2 esports matches, implemented using Proximal Policy Optimization (PPO). We use a sample model provided by [Nikhil](https://github.com/nikhilbarhate99/PPO-PyTorch) that calculates advantage with Monte Carlo. Q-Bet ingests round-level JSON game data, computes both raw and crafted feature vectors (including market-signal features like Expected Value and Kelly Criterion), and trains discrete-action-space PPO agents under different reward-function formulations. The goal is to learn when to bet (and how much) to maximize overall bankroll growth.

The following `README.md` provides a quick breakdown of what happens in our application. For further learning or clarification, please reference our paper in `Q-Bet/documentation/ppo-paper.pdf`.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
4. [Data Preparation](#data-preparation)
   - [Match JSON Files](#match-json-files)
   - [Winners Lookup](#winners-lookup)
6. [Feature Engineering](#feature-engineering)
5. [Usage](#usage)
   - [Configuring Hyperparameters](#configuring-hyperparameters)
   - [Training an Agent](#training-an-agent)
   - [Evaluating an Agent](#evaluating-an-agent)
   - [Visualizing Results](#visualizing-results)
10. [Experiment Results](#experiment-results)
11. [Contributing](#contributing)
   - [How to Contribute](#how-to-contribute)

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

For python code:

- **Python 3.8 +**
- **PyTorch ≥ 1.9** (CPU or CUDA)
- **NumPy**
- **pandas**
- **scikit-learn** (for any clustering or normalization routines)
- **Matplotlib** (for plotting)
- **PlayWright** (web-scraping)

```bash
# pip dependencies
pip install torch numpy scikit-learn matplotlib
```

### Installation

Copy the repository to your folder of choice

```bash
# navigate to your folder of choice
cd dev

# clone using HTTP
git clone https://github.com/hoNATHAN/Q-Bet.git .

# clone using SSH
git clone git@github.com:hoNATHAN/Q-Bet.git .
```

## Data Preparation

Data is webscraped from two websites. 

- [bo3](https://bo3.gg/): where match data for rounds are scraped
- [oddsportal](https://www.oddsportal.com/esports/): where match odds are scraped

### Match JSON Files

Go into the `q-bet-scraper` directory to run `scrape.py`

```bash
# go to root dir if not already there
cd Q-Bet

# cd into the scraper dir
cd q-bet-scraper

# run scrape.py using your python manager of choice
python scrape.py
python3 scrape.py
uv run scrape.py # may want to uv venv first
```

This should populate raw JSON files in the `Q-Bet/data/match` and `Q-Bet/data/odds`.

### Winners Lookup

Our code requires preprocessing the raw scraped JSON to build a dictionary of winners. This helps during training phase to quick lookup if the agent bets correctly on the winning team.

```bash
cd Q-Bet/q-bet-analysis

# run generate_winners.py using your python manager of choice
python generate_winners.py
python3 generate_winners.py
uv run generate_winners.py # may want to uv venv first
```

## Feature Engineering

As stated above, we pull several raw game states and process economy to sophisticated market signals.

```bash
cd Q-Bet/q-bet-agent/feature_vector.py
```

The file has well documented comments to help guide you on what happens. Essentially, `feature_vector.py` has two feature vector helpers. One that calculates a tensor for market signals and one for raw game statistics. This is later benchmarked for performance across different agents.

`train.py` will feature vector the game states. Our JSON match data is aligned with the odds data and tensors are created for episodic training. 

**Keep in mind that our states are defined as the end of a round in a CS2 match**

## Usage

Agent code is defined in `Q-Bet/q-bet-agent`.

### Configuring Hyperparameters

Our hyperparameters are as defined.

### Training an Agent

```bash
cd Q-Bet/q-bet-agent

# To train and test, run 
python train.py --reward_scheme ['basic', 'binary', 'complex'] --action-space ['basic', 'complex_discrete', 'complex_continuous'] --resume --initial_balance float --feature-type ['crafted', 'raw']

python3 train.py --reward_scheme ['basic', 'binary', 'complex'] --action-space ['basic', 'complex_discrete', 'complex_continuous'] --resume --initial_balance float --feature-type ['crafted', 'raw']

uv run train.py --reward_scheme ['basic', 'binary', 'complex'] --action-space ['basic', 'complex_discrete', 'complex_continuous'] --resume --initial_balance float --feature-type ['crafted', 'raw']
```

### Evaluating an Agent

We evaluate agents by analyzing the graph outputs.

### Visualizing Results 

To output all the graphs for agent performance. 

```bash
cd Q-Bet/q-bet-analysis
python generate_graph.py
python3 generate_graph.py
uv run generate_graph.py
```

To output graphs to visualize feature distributions.

```bash
cd Q-Bet/q-bet-analysis
python feature_distribution.py
python3 feature_distribution.py
uv run feature_distribution.py
```

## Contributing

Thank you for your interest in contributing to this project! Whether you're fixing bugs, adding features, improving documentation, or sharing ideas, your help is appreciated.

### How to Contribute

1. **Fork the Repository**  

   Click the "Fork" button at the top of the page to create a copy of the repository under your GitHub account.

2. **Clone Your Fork**  

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```