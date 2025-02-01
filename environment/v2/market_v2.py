from typing import List, Optional, Dict
from dataclasses import dataclass
import random
import logging
from environment.player import Player
from environment.factory import create_player

@dataclass
class MarketConfig:
    """Configuration parameters for the market"""
    min_refresh_rate: float = 0.1  # Minimum percentage of players to refresh
    max_refresh_rate: float = 0.33  # Maximum percentage of players to refresh
    min_price_volatility: float = 0.95  # Minimum price multiplier
    max_price_volatility: float = 1.05  # Maximum price multiplier

class MarketException(Exception):
    """Custom exception for market-related errors"""
    pass

class Market:
    def __init__(self, market_size: int, pipeline, config: MarketConfig = None):
        """
        Initialize the market with a predefined number of players.
        
        Args:
            market_size: Number of players in the market.
            pipeline: The data pipeline to fetch player data.
            config: Market configuration parameters.
        
        Raises:
            ValueError: If market_size is less than 1.
        """
        if market_size < 1:
            raise ValueError("Market size must be at least 1")
        
        self.market_size = market_size
        self.pipeline = pipeline
        self.config = config or MarketConfig()
        self.players: List[Optional[Player]] = []
        self.transaction_history: List[Dict] = []
        self.week_number: int = 0
        
        self._logger = logging.getLogger(__name__)
        self.initialize()

    def initialize(self) -> None:
        """Generate the initial list of players in the market."""
        self.players = []
        for _ in range(self.market_size):
            try:
                player = create_player("market", self.pipeline)
                self.players.append(player)
            except Exception as e:
                self._logger.error(f"Failed to create player: {str(e)}")
                self.players.append(None)

    def get_player(self, player_index: int) -> Optional[Player]:
        """
        Retrieve a player from the market by index.
        
        Args:
            player_index: Index of the player to retrieve.
        
        Returns:
            Player instance or None if not found.
            
        Raises:
            IndexError: If player_index is out of bounds.
        """
        if not 0 <= player_index < len(self.players):
            raise IndexError(f"Player index {player_index} out of range")
        return self.players[player_index]

    def remove_player(self, player_index: int) -> None:
        """
        Remove a player from the market and replace with a new one.
        
        Args:
            player_index: Index of the player to remove.
            
        Raises:
            IndexError: If player_index is out of bounds.
        """
        if not 0 <= player_index < len(self.players):
            raise IndexError(f"Player index {player_index} out of range")
            
        old_player = self.players[player_index]
        if old_player:
            self.transaction_history.append({
                'week': self.week_number,
                'type': 'remove',
                'player_id': old_player.id,
                'player_name': old_player.name,
                'price': old_player.release_clause
            })
            
        try:
            self.players[player_index] = create_player("market", self.pipeline)
        except Exception as e:
            self._logger.error(f"Failed to create replacement player: {str(e)}")
            self.players[player_index] = None

    def get_players(self) -> List[Player]:
        """
        Get all valid players currently in the market.
        
        Returns:
            List of Player objects, excluding None values.
        """
        return [player for player in self.players if player is not None]

    def get_available_slots(self) -> int:
        """
        Get the number of available slots in the market.
        
        Returns:
            Number of None values in the players list.
        """
        return self.players.count(None)

    def update_prices(self) -> None:
        """Update player prices based on performance and market volatility."""
        for player in self.get_players():
            volatility = random.uniform(
                self.config.min_price_volatility,
                self.config.max_price_volatility
            )
            performance_modifier = 1.0 + (player.points / 100)  # Adjust based on points
            new_price = player.release_clause * volatility * performance_modifier
            player.release_clause = round(new_price, 2)

    def refresh(self) -> None:
        """
        Refresh the market by:
        1. Replacing some players with new ones
        2. Updating prices for remaining players
        3. Incrementing week counter
        """
        self.week_number += 1
        self.update_prices()
        
        num_to_replace = random.randint(
            int(len(self.players) * self.config.min_refresh_rate),
            int(len(self.players) * self.config.max_refresh_rate)
        )
        
        indices_to_replace = random.sample(range(len(self.players)), num_to_replace)
        for idx in indices_to_replace:
            self.remove_player(idx)

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """
        Find a player by name.
        
        Args:
            name: Name of the player to find.
            
        Returns:
            Player instance or None if not found.
        """
        for player in self.get_players():
            if player.name.lower() == name.lower():
                return player
        return None

    def get_players_by_price_range(self, min_price: float, max_price: float) -> List[Player]:
        """
        Get players within a specific price range.
        
        Args:
            min_price: Minimum price.
            max_price: Maximum price.
            
        Returns:
            List of players within the price range.
        """
        return [
            player for player in self.get_players()
            if min_price <= player.release_clause <= max_price
        ]

    def get_transaction_history(self, last_n_weeks: Optional[int] = None) -> List[Dict]:
        """
        Get market transaction history.
        
        Args:
            last_n_weeks: Optional number of weeks to limit history to.
            
        Returns:
            List of transaction dictionaries.
        """
        if last_n_weeks is None:
            return self.transaction_history
        
        current_week = self.week_number
        return [
            t for t in self.transaction_history
            if current_week - t['week'] <= last_n_weeks
        ]

    def __len__(self) -> int:
        """Return the number of valid players in the market."""
        return len(self.get_players())

    def __str__(self) -> str:
        """Return a string representation of the market."""
        return f"Market(size={self.market_size}, active_players={len(self)})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the market."""
        return (f"Market(size={self.market_size}, "
                f"active_players={len(self)}, "
                f"week={self.week_number})")