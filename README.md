# Fantasy RL - Reinforcement Learning for Fantasy Football Management

A reinforcement learning project that trains AI agents to optimize fantasy football team management through intelligent player trading, team composition, and strategic decision-making.

## Project Overview

Fantasy RL simulates a fantasy football environment where AI agents learn to:
- Build optimal team compositions
- Make strategic player purchases and sales
- Manage limited budgets effectively
- Maximize team performance points
- Compete in fantasy football leagues

## Architecture

## Core Components

- **Environment** (`environment/`): Custom Gym environment simulating fantasy football mechanics
- **Algorithms** (`algorithms/`): Implementation of various RL algorithms
- **API** (`api/`): Data pipeline for player statistics and team information
- **Training Scripts** (`train/`): Entry points for training different RL models

## Supported RL Algorithms

- **DQN** (Deep Q-Network): Neural network-based Q-learning
- **PPO** (Proximal Policy Optimization): Policy gradient method
- **REINFORCE**: Basic policy gradient algorithm
- **SARSA**: State-Action-Reward-State-Action learning

## etting Started

## Prerequisites

- Python 3.10+
- uv (Python package manager)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd fantasy-rl

# Install dependencies using uv
uv sync
```

## Dependencies

Key packages include:
- `numpy`, `pandas`, `scipy` for data processing
- `matplotlib`, `altair` for visualization
- `requests` for API data fetching
- `mlflow` for experiment tracking
- `tqdm` for progress bars

## Usage

## Training an Agent

```bash
# Train a DQN agent
python train/train_dqn.py

# Train a PPO agent
python train/train_ppo.py

# Train a REINFORCE agent
python train/train_reinforce.py

# Train a SARSA agent
python train/train_sarsa.py
```

## Environment Actions

The environment supports three action types:
1. **Sell Player**: Remove a player from team (action indices 0-10)
2. **Buy Player**: Purchase a player from market (action indices 11-35)
3. **Finish Week**: Complete the current week's transfers (action index 36)

## State Representation

The environment state includes:
- Team player metrics (11 players  17 metrics each)
- Market player metrics (25 players  17 metrics each)
- Current budget information
- All normalized to [0,1] range

## Environment Details

## Game Rules

- **Team Size**: 11 players (minimum 8 required)
- **Market Size**: 25 available players
- **Initial Budget**: $100,000
- **Max Actions per Week**: 21
- **Player Metrics**: 17 performance indicators per player

## Reward System

- **Buying**: Positive reward based on player performance relative to team max
- **Selling**: Negative reward based on player performance relative to team max
- **Invalid Actions**: -1 reward penalty
- **Week Completion**: Reward based on total team performance points

## Project Structure

```
fantasy-rl/
 algorithms/          # RL algorithm implementations
    DQN/            # Deep Q-Network
    PPO/            # Proximal Policy Optimization
    REINFORCE/      # Policy gradient
    SARSA/          # SARSA learning
 api/                # Data fetching and management
    common/         # Static data (players, teams)
    data/           # Historical match data
    src/            # API services
 environment/        # Gym environment implementation
 train/              # Training scripts
 logs/               # Training logs and visualizations
 actions/            # Utility scripts
 docs/               # Documentation
```

## Training Results

Training logs and reward plots are automatically saved to the `logs/` directory, organized by algorithm and timestamp. Each training session generates:
- Reward progression plots
- Model checkpoints
- Training statistics

## Experiments

The project uses MLflow for experiment tracking. Key metrics monitored:
- Episode rewards
- Training loss
- Team performance
- Budget utilization

## ' Configuration

Environment parameters can be adjusted in `environment/environment.py`:
- `TEAM_SIZE`: Number of players in team
- `MARKET_SIZE`: Number of players in market
- `INITIAL_BUDGET`: Starting budget amount
- `MAX_ACTIONS_PER_WEEK`: Transfer limit per week

## Data Sources

The project includes:
- Player statistics from multiple seasons
- Team information and compositions
- Historical match data
- Market valuation data

## Development Status

This is an active research project exploring the application of reinforcement learning to fantasy sports management. The codebase supports experimentation with different RL algorithms and environment configurations.

## Contributing

This project is designed for research and experimentation in reinforcement learning applications to sports analytics and game theory.

## License

See LICENSE file for details.