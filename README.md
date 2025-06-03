# Counter-Strike 2 eSports Betting Agent

**CS 486 Final Project — Drexel University**

This project implements a **reinforcement learning agent** that places **bets** on professional _Counter-Strike 2_ esports matches. The goal is to learn optimal betting strategies by balancing **profit maximization** with **risk management**.

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

- Match data form bo3.gg and Betting odds Data from oddsportal.com
- PPO-based reinforcement learning model
- Custom reward function that simulates profit/loss from bets

---

## Objectives

- Apply RL algorithms to a real-world domain (sports betting)
- Analyze decision timing, expected value, and model confidence

---

## Running Locally

To run the agent
cd into q-bet-agent
To train and test, run python train.py --reward_scheme ['basic', 'binary', 'complex'] --action-space ['basic', 'complex_discrete', 'complex_continuous'] --resume --initial_balance float --feature-type ['crafted', 'raw']

To run the web scraper
cd into q-bet-scraper
run python scrape.py
