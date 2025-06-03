# League of Legends eSports Moneyline Betting Agent

**CS 486 Final Project — Drexel University**

This project implements a **reinforcement learning agent** that places **moneyline bets** on professional _League of Legends_ esports matches. The goal is to learn optimal betting strategies by balancing **profit maximization** with **risk management**.

---

## Course Info

- **Course**: CS 486 — Introduction to Artificial Intelligence
- **Institution**: Drexel University
- **Term**: Spring 2025
- **Team**: Nathan Ho, Matthew Protacio, Alexey Kuraev

---

## TODO: Update with actual project stuff

## Project Overview

We train a DRL (Deep Reinforcement Learning) agent that:

- Observes match state and betting odds in real time
- Decides **when** and **how** to place bets
- Learns to maximize **expected return** over time

Core components:

- Match state embeddings from LoL esports data
- A3C/DQN-based reinforcement learning model
- Custom reward function that simulates profit/loss from bets

---

## Objectives

- Apply RL algorithms to a real-world domain (sports betting)
- Analyze decision timing, expected value, and model confidence

---

## Running Locally

# TODO write instructions to run website

To run the website

# TODO write instructions to run agent

To train the RL betting agent, navigate to the `q-bet-agent` directory and run:
  ```pwsh
  cd q-bet-agent
  python train.py \
    --reward-scheme <binary|complex> \
    --action-space <basic|complex_discrete|complex_continuous> \
    --feature-type <crafted|raw> \
    [--initial-balance <float>] \
    [--resume]
  ```

  Flags:
  - `--reward-scheme`: Reward function to use (`basic`, `binary`, or `complex`).
  - `--action-space`: Action space type (`basic`, `complex_discrete`, or `complex_continuous`).
  - `--feature-type`: Feature vectors (`crafted` or `raw`).
  - `--initial-balance`: Starting bankroll (default: `1000.0`).
  - `--resume`: Resume training from the latest checkpoint.

# TODO write instructions to run web scraper

To run the web scraper
