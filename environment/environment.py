import os 
import time
import numpy as np
import gymnasium as gym

from pipeline import Pipeline
from environment.team import Team
from environment.market import Market

METRICS_SIZE = 17
TEAM_SIZE = 11
MIN_TEAM_SIZE = 8
MARKET_SIZE = 25
INITIAL_BUDGET = 100000.0
MAX_ACTIONS_PER_WEEK = 21

class Environment(gym.Env):
    def __init__(self, pipeline: Pipeline):
        super(Environment, self).__init__()
        self.pipeline = pipeline
        self.metrics_size = METRICS_SIZE
        self.team_size = TEAM_SIZE
        self.market_size = MARKET_SIZE
        self.budget = INITIAL_BUDGET
        self.team = Team(team_size=TEAM_SIZE, pipeline=pipeline)
        self.market = Market(market_size=MARKET_SIZE, pipeline=self.pipeline)
        self.actions = []

        # Define action space
        self.action_space = gym.spaces.Discrete(self.team_size + self.market_size + 1)

        # Define observation space
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=[(self.team_size + self.market_size + 1) * self.metrics_size])

    def reset(self):
        self.budget = INITIAL_BUDGET
        self.team.reset()
        self.market.reset()
        self.actions = []
        return self.get_state()

    def step(self, action_value):
        # Check if max actions per week has been reached
        if len(self.actions) >= MAX_ACTIONS_PER_WEEK:
            return self.get_state(), 0.0, True, {}
        
        # Initialize action
        action = {
            'type': None,
            'player_index': None,
            'player': None,
            'reward': 0,
            'week_done': False,
            'valid': True,
            'message': '',
        }

        # Decode action
        if action_value < self.team_size:
            action['type'] = "sell"
            action['player_index'] = action_value
            action['player'] = self.team.get_player(action['player_index'])
        elif action_value >= self.team_size and action_value < self.team_size + self.market_size:
            action['type'] = "buy"
            action['player_index'] = action_value - self.team_size
            action['player'] = self.market.get_player(action['player_index'])
        elif action_value == self.team_size + self.market_size:
            action['type'] = "finish"
            action['player_index'] = -1
            action['player'] = None
        else:
            raise ValueError(f"Invalid action index selected: {action_value}")

        # Execute action
        if action['type'] == "sell":  # Sell
            if self.team.get_players(return_none=True).count(None) >= TEAM_SIZE - MIN_TEAM_SIZE:
                # Penalize if selling reduces team below the minimum size
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "Cannot sell, team size would drop below the minimum"
            elif action['player'].player_type == 'empty':
                # Penalize selling an empty slot
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "Cannot sell an empty player"
            else:
                # Get max player points
                max_points = max(self.team.get_players(), key=lambda x: x.points if x is not None else 0).points
                # Reward based on player performance metrics
                # action['reward'] += (max_points - action['player'].points)
                action['reward'] -= action['player'].points / max_points
                self.budget += action['player'].release_clause
                self.team.remove_player(action['player_index'])
                action['message'] = f"Sold {action['player'].player_id} for ${action['player'].release_clause:,.2f}"

        elif action['type'] == "buy":  # Buy
            if None not in self.team.get_players(return_none=True):
                # Penalize if no space in the team
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "No space in the team"
            elif self.budget < action['player'].release_clause:
                # Penalize if insufficient budget
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "Insufficient budget"
            elif action['player'].player_type == 'empty':
                # Penalize buying an empty slot
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "Cannot buy an empty player"
            else:
                max_points = max(self.team.get_players(), key=lambda x: x.points if x is not None else 0).points
                # Reward based on player performance metrics
                action['reward'] += action['player'].points / max_points
                self.budget -= action['player'].release_clause
                self.team.add_player(action['player'])
                self.market.remove_player(action['player_index'])
                action['message'] = f"Bought {action['player'].player_id} for ${action['player'].release_clause:,.2f}"

        elif action['type'] == "finish":  # Finish week
            if self.team.get_players(return_none=True).count(None) > 0:
                # Penalize for incomplete team
                action['reward'] -= -1
                action['week_done'] = True
                action['message'] = f"Week ended with missing players"
            elif self.budget < 0:
                # Penalize for negative budget
                action['reward'] -= 1
                action['week_done'] = True
                action['message'] = "Insufficient budget"
            else:
                # Reward based on team performance
                performance_points = self.team.get_points()
                action['reward'] += performance_points
                action['week_done'] = True
                action['message'] = f"Finish week"

        # Add action to history
        self.actions.append(action)

        # Return state, reward, done, info
        return self.get_state(), action['reward'], action['week_done'], {}

    def render(self, mode='human'):
        os.system('clear' if os.name == 'posix' else 'cls')  # Clear the terminal
        print(f"Budget: ${self.budget:,.2f}")
        print("\nTeam:")
        self._render_team()
        print("\nMarket:")
        self._render_market()
        print("\nActions:")
        self._render_actions()

    def get_state(self):
        # Get team players metrics
        team = np.array([player.metrics for player in self.team.get_players() if player is not None])
        # Normalize team metrics
        team = team.astype(np.float64) / np.max(team, axis=0)
        # Get market players metrics
        market = np.array([player.metrics for player in self.market.get_players() if player is not None])
        # Normalize market metrics
        market = market.astype(np.float64) / np.max(market, axis=0)

        budget = np.ones((1,self.metrics_size)) * self.budget
        # Create state 2d matrix of team, market players and budget
        state = np.concatenate([team, market, budget])
        
        return state.flatten()

    def _render_team(self):
        for idx, player in enumerate(self.team.get_players()):
            self._render_player(player)

    def _render_market(self):
        for idx, player in enumerate(self.market.get_players()):
            self._render_player(player)

    def _render_player(self, player):
        print(f"{player.player_id:20} | Points: {player.points:<4} | Value: ${player.release_clause:,.2f}")

    def _render_actions(self):
        for idx, action in enumerate(self.actions):
            print(f"Action {idx}: {action['message']} | Reward {action['reward']}")
    