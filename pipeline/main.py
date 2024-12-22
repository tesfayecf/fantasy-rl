import random
import logging
from enum import Enum
from functools import lru_cache
from typing import List, Dict, Any, Tuple

from api import API

class Position(Enum):
    """
    Enum representing player positions with corresponding ID codes.
    """
    NONE = None
    PORTERO = '1'
    DEFENSA = '2'
    CENTROCAMPISTA = '3'
    DELANTERO = '4'
    ENTRENADOR = '5'

class Pipeline:
    """
    Fantasy Football Data Pipeline for Reinforcement Learning.

    Features:
    - Player data pre-fetching and caching.
    - Intelligent selection to avoid duplicate data.
    - In-memory buffer for quick access.
    """

    def __init__(self, buffer_size: int = 50, log_level: str = 'INFO'):
        self.buffer_size = buffer_size

        # Logging setup
        logging.basicConfig(level=getattr(logging, log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)

        # Core components
        self.api = API()
        self.selected_players = set()
        self.selected_weeks = set()

        # Pre-fetching setup
        # self.prefetch_queue = queue.Queue(maxsize=self.buffer_size)
        # self.prefetch_stop_event = threading.Event()
        # self.prefetch_thread = threading.Thread(target=self._prefetch_data, daemon=True)

    def init(self):
        try:
            self.api.init()
            # self.prefetch_thread.start()
            self.logger.info("Pipeline initialized.")
        except Exception as e:
            self.logger.error(f"API initialization failed: {e}")
            raise

    def get_player(self, position: Position = Position.NONE) -> Tuple[Dict[str, float], int]:
        """
        Get player performance data and expected next week's points.
        """
        player_id = self._select_unique_player(position)
        week_id = self._select_unique_week()
        played = self.api.players.didPlayerPlay(player_id, week_id)
        if not played:
            return self.get_player(position)
        metrics, next_week_points = self._get_player_data(player_id, week_id)
        if metrics == None or next_week_points == None:
            return self.get_player(position)
        self.logger.debug(f"Player: {player_id}, Week: {week_id}, Next Week Points: {next_week_points}")
        return metrics, next_week_points

    def get_team(self, formation: str) -> List[Dict[str, Any]]:
        """
        Build a team based on a formation (e.g., '1-4-3-3').
        """
        try:
            positions = list(map(int, formation.split('-')))
            if len(positions) != 4 or sum(positions) != 11:
                raise ValueError(f"Invalid formation: {formation}. Must be '1-4-3-3' with 11 players.")

            team = []
            position_mapping = [
                (Position.PORTERO, positions[0]),
                (Position.DEFENSA, positions[1]),
                (Position.CENTROCAMPISTA, positions[2]),
                (Position.DELANTERO, positions[3]),
            ]
            for position, count in position_mapping:
                for _ in range(count):
                    team.append(self._select_unique_player(position))
            return team
        except Exception as e:
            self.logger.error(f"Error creating team with formation {formation}: {e}")
            raise

    def _select_unique_week(self) -> int:
        """
        Select a unique week ID.
        """
        weeks = self.api.teams.getWeekIds()
        available_weeks = [w for w in weeks[1:-1] if w not in self.selected_weeks]
        if not available_weeks:
            self.selected_weeks.clear()
            available_weeks = weeks[1:-1]
        week_id = random.choice(available_weeks)
        self.selected_weeks.add(week_id)
        return week_id

    def _select_unique_player(self, position: Position = Position.NONE) -> int:
        """
        Select a unique player based on position.
        """
        players = self.api.players.getPlayersIds()
        if position != Position.NONE:
            players = [p for p in players if p['positionId'] == position.value]
        available_players = [p for p in players if int(p) not in self.selected_players]
        if not available_players:
            self.selected_players.clear()
            available_players = players
        player = random.choice(available_players)
        self.selected_players.add(int(player))
        return int(player)

    def _get_player_data(self, player_id: int, week_id: int) -> Tuple[Dict[str, float], int]:
        """
        Get player performance data and expected next week's points.
        """
        metrics = self._get_player_performance_metrics(player_id, week_id - 1)
        if metrics == None:
            return None, None
        next_week_stats = self.api.players.getStatsForWeek(player_id, week_id)
        if next_week_stats == None:
            return None, None
        return metrics, next_week_stats.get('totalPoints', 0)

    @lru_cache(maxsize=1000)
    def _get_player_performance_metrics(self, player_id: int, week_id: int) -> Dict[str, float]:
        """
        Get player performance metrics.
        """
        try:
            return {
                'total_minutes_played': self.api.players.getTotalMinutesPlayed(player_id, week_id),
                'total_goals_scored': self.api.players.getTotalGoals(player_id, week_id),
                'total_assists': self.api.players.getTotalAssists(player_id, week_id),
                'total_scoring_attempts': self.api.players.getTotalTotalScoringAttempts(player_id, week_id),
                'total_effective_clearances': self.api.players.getTotalEffectiveClearances(player_id, week_id),
                'total_ball_recoveries': self.api.players.getTotalBallRecovery(player_id, week_id),
                'total_goals_conceded': self.api.players.getTotalGoalsConceded(player_id, week_id),
                'yellow_cards': self.api.players.getTotalYellowCards(player_id, week_id),
                'red_cards': self.api.players.getTotalRedCards(player_id, week_id),
                'total_possessions_lost': self.api.players.getTotalPossessionLostAll(player_id, week_id),
                'penalty_area_entries': self.api.players.getTotalPenaltyAreaEntries(player_id, week_id),
                'total_points_earned': self.api.players.getTotalPoints(player_id, week_id),
                'total_matches_played': self.api.players.getTotalGamesPlayed(player_id, week_id),
                'penalties_won': self.api.players.getTotalPenaltiesWon(player_id, week_id),
                'penalties_conceded': self.api.players.getTotalPenaltiesConceded(player_id, week_id),
                'own_goals': self.api.players.getTotalOwnGoals(player_id, week_id),
                'market_value': self.api.players.getMarketValue(player_id),
            }
        except Exception as e:
            self.logger.warning(f"Error retrieving metrics for player {player_id}, week {week_id}: {e}")
            return None

    def close(self):
        """
        Stop pre-fetching and release resources.
        """
        # self.prefetch_stop_event.set()
        # self.prefetch_thread.join()
        self.logger.info("Pipeline resources closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
