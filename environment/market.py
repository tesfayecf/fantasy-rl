import random

from environment.player import Player
from environment.factory import create_player

class Market:
    def __init__(self, market_size: int, pipeline):
        """
        Initialize the market with a predefined number of players.
        :param market_size: Number of players in the market.
        :param pipeline: The data pipeline to fetch player data.
        """
        self.market_size = market_size
        self.pipeline = pipeline
        self.players = self._initialize_market()

    def _initialize_market(self):
        """
        Generate the initial list of players in the market.
        :return: List of Player objects.
        """
        return [create_player("market", self.pipeline) for _ in range(self.market_size)]

    def get_player(self, player_id):
        """
        Retrieve a player from the market by ID.
        :param player_id: The ID of the player to retrieve.
        :return: Player instance or None if not found.
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def add_player(self, player: Player):
        """
        Add a player to the market.
        :param player: The Player instance to add.
        """
        if len(self.players) < self.market_size:
            self.players.append(player)

    def remove_player(self, player: Player):
        """
        Remove a player from the market.
        :param player: The Player instance to remove.
        """
        self.players = [p for p in self.players if p.player_id != player.player_id]

    def refresh_market(self):
        """
        Refresh the market by replacing some players with new ones.
        Useful for simulating new players entering the market every week.
        """
        num_to_replace = random.randint(1, len(self.players) // 3)  # Replace ~1/3 of the market
        for _ in range(num_to_replace):
            player_to_remove = random.choice(self.players)
            self.remove_player(player_to_remove)
            self.add_player(self._create_player())

    def get_all_players(self):
        """
        Get all players currently in the market.
        :return: List of Player objects.
        """
        return self.players
