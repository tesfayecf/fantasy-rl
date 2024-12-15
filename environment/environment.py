import os 
import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from pipeline import Pipeline
from environment.market import Market
from environment.factory import create_player

TEAM_SIZE = 11
MARKET_SIZE = 50
INITIAL_BUDGET = 100000.0

class Environment(gym.Env):
    def __init__(self, pipeline: Pipeline):
        super(Environment, self).__init__()
        self.pipeline = pipeline

        self.team_size = TEAM_SIZE
        self.market_size = MARKET_SIZE
        self.budget = INITIAL_BUDGET
        self.team = []  # List of Player instances
        self.market = Market(market_size=MARKET_SIZE, pipeline=self.pipeline)
        self.week_id = 1

        # Define action space
        self.action_space = spaces.Tuple((
            spaces.Discrete(4),  # Action type: Buy, Sell, Adjust, Hold
            spaces.Discrete(self.team_size + self.market_size),  # Player index
            spaces.Box(low=0.0, high=100.0, shape=(1,))  # Release clause percentage adjustment
        ))

        # Define observation space
        self.observation_space = spaces.Dict({
            'team': spaces.Box(low=0, high=1, shape=(self.team_size, len(self._get_player_features()))),
            'budget': spaces.Box(low=0, high=1, shape=(1,)),
            'market': spaces.Box(low=0, high=1, shape=(self.market_size, len(self._get_player_features()))),
        })

    def _get_player_features(self):
        return [
            'total_minutes_played', 'total_goals_scored', 'total_assists',
            'total_scoring_attempts', 'total_effective_clearances',
            'total_ball_recoveries', 'total_goals_conceded', 'yellow_cards',
            'red_cards', 'total_possessions_lost', 'penalty_area_entries',
            'total_points_earned', 'total_matches_played', 'penalties_won',
            'penalties_conceded', 'own_goals', 'market_value',
        ]

    def reset(self):
        self.budget = INITIAL_BUDGET
        self.team = self._initialize_team()
        self.market.refresh_market()  # Refresh the market at reset
        self.week_id = 1
        return self._get_state()

    def _initialize_team(self):
        return [create_player('team', self.pipeline) for _ in range(self.team_size)]

    def _get_state(self):
        team_data = np.array([player.metrics for player in self.team])
        market_data = np.array([player.metrics for player in self.market.get_all_players()])
        return {
            'team': team_data,
            'budget': np.array([self.budget]),
            'market': market_data,
        }

    def step(self, action):
        action_type, player_index, optional_value = action
        reward = 0

        if action_type == 0:  # Buy
            market_index = player_index - len(self.team)
            if market_index >= 0 and market_index < len(self.market.players):
                player = self.market.players[market_index]
                if self.budget >= player.release_clause:
                    player.buy(buyer_team=self, price=player.release_clause)
                    self.market.remove_player(player)
                    self.team.append(player)
                    self.budget -= player.release_clause
                    reward += player.stats['total_points_earned']

        elif action_type == 1:  # Sell
            if player_index < len(self.team):
                player = self.team[player_index]
                self.budget += player.release_clause
                player.reset()  # Reset player state
                self.team.remove(player)

        elif action_type == 2:  # Adjust Clause
            if player_index < len(self.team):
                player = self.team[player_index]
                new_clause = player.release_clause * (1 + optional_value[0] / 100)
                player.align_clause(new_clause=new_clause)
                reward -= 0.1  # Penalty for adjustment

        elif action_type == 3:  # Hold
            pass  # No changes

        # Update the market and team players for the next week
        self.week_id += 1
        for player in self.team:
            player_data = self.pipeline.get_player(player.player_id, self.week_id)
            player.metrics.update(player_data)
        self.market.refresh_market()

        # Calculate cumulative reward
        reward += sum(player.metrics['total_points_earned'] for player in self.team)
        done = self.week_id > 38  # Example end condition
        return self._get_state(), reward, done, {}

    def render(self, mode='human'):
        os.system('clear' if os.name == 'posix' else 'cls')  # Clear the terminal
        print(f"=== Week {self.week_id} ===")
        print(f"Budget: ${self.budget:,.2f}")
        print("\nYour Team:")
        self._render_team()
        print("\nMarket:")
        self._render_market()
        print("\nActions: [0] Buy, [1] Sell, [2] Adjust Clause, [3] Hold")
        time.sleep(0.5)  # Pause for animation effect

    def _render_team(self):
        for idx, player in enumerate(self.team):
            print(f"{idx + 1:2d}. {player.name:20} | Points: {player.metrics['total_points_earned']:<4} "
                  f"| Value: ${player.release_clause:,.2f}")

    def _render_market(self):
        for idx, player in enumerate(self.market.get_all_players()):
            print(f"{idx + 1:2d}. {player.name:20} | Points: {player.metrics['total_points_earned']:<4} "
                  f"| Value: ${player.release_clause:,.2f}")