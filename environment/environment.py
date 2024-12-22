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
MARKET_SIZE = 15
INITIAL_BUDGET = 100000.0
MAX_ACTIONS_PER_WEEK = 10

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
        self.observation_space = gym.spaces.Dict({
            'team': gym.spaces.Box(low=0, high=1, shape=(self.team_size, self.metrics_size)),
            'market': gym.spaces.Box(low=0, high=1, shape=(self.market_size, self.metrics_size)),
            'budget': gym.spaces.Box(low=0, high=1, shape=(1,)),
        })

    def reset(self):
        self.budget = INITIAL_BUDGET
        self.team.reset()
        self.market.reset()
        self.actions = []
        return self._get_state()

    def step(self, action_value):
        # Check if max actions per week has been reached
        if len(self.actions) >= MAX_ACTIONS_PER_WEEK:
            return self._get_state(), 0.0, True, {}

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
            # Check team has enough players
            if self.team.get_players(return_none=True).count(None) >= TEAM_SIZE - MIN_TEAM_SIZE:
                # Penalize no players in team
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "Not enough players in team"
            else:
                # Add player value to budget
                self.budget += action['player'].release_clause
                # Remove player from team
                self.team.remove_player(action['player_index'])
                # Small reward for doing valid action
                action['reward'] += 0.1
                action['message'] = f"Sold {action['player'].player_id} for ${action['player'].release_clause:,.2f}"
        
        elif action['type'] == "buy":  # Buy
            # Check team has space
            if None not in self.team.get_players(return_none=True):
                # Penalize no space in team
                action['reward'] -= 1
                action['valid'] = False
                action['message'] = "No space in team"
            else:
                # Check budget is enough
                if self.budget < action['player'].release_clause:
                    # Penalize insufficient budget
                    action['reward'] -= 1
                    action['valid'] = False
                    action['message'] = "Insufficient budget"
                if action['player'].player_type == 'empty':
                    # Penalize buying empty player
                    action['reward'] -= 1
                    action['valid'] = False
                    action['message'] = "Cannot buy empty player"
                else:
                    # Subtract player budget from budget
                    self.budget -= action['player'].release_clause
                    # Add player to team
                    self.team.add_player(action['player'])
                    # Remove player from market
                    self.market.remove_player(action['player_index'])
                    # Small reward for buying a player
                    action['reward'] += 0.1
                    action['message'] = f"Bought {action['player'].player_id} for ${action['player'].release_clause:,.2f}"

        elif action['type'] == "finish":  # Finish week
            # Check if valid finish
            if None in self.team.get_players(return_none=True):
                # Penalize invalid finish
                action['reward'] -= 1
                action['week_done'] = True
                action['message'] = "Not enough players in team"
            if self.budget < 0:
                # Penalize invalid finish
                action['reward'] -= 1
                action['week_done'] = True
                action['message'] = "Insufficient budget"
            else:
                action['reward'] += self.team.get_points()
                action['week_done'] = True
                action['message'] = f"Finished week with {self.team.get_points()} points"

        # Add action to history
        self.actions.append(action)

        # Return state, reward, done, info
        return self._get_state(), action['reward'], action['week_done'], {}

    def render(self, mode='human'):
        os.system('clear' if os.name == 'posix' else 'cls')  # Clear the terminal
        print(f"Budget: ${self.budget:,.2f}")
        print("\nYour Team:")
        self._render_team()
        print("\nMarket:")
        self._render_market()
        print("\nActions:")
        self._render_actions()

        time.sleep(0.5)  # Pause for animation effect

    def _get_state(self):
        return {
            'team': np.array([player.metrics for player in self.team.get_players()]),
            'market': np.array([player.metrics for player in self.market.get_players()]),
            'budget': np.array([self.budget]),
        }
    
    def _render_actions(self):
        for idx, action in enumerate(self.actions):
            print(f"Action {idx}: {action['message']} | Reward {action['reward']}")
    
    def _render_team(self):
        for idx, player in enumerate(self.team.get_players()):
            self._render_player(player)

    def _render_market(self):
        for idx, player in enumerate(self.market.get_players()):
            self._render_player(player)

    def _render_player(self, player):
        print(f"{player.player_id:20} | Points: {player.points:<4} | Value: ${player.release_clause:,.2f}")