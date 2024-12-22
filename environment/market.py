import random

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
        self.players = []
        
        self.initialize()

    def initialize(self):
        """
        Generate the initial list of players in the market.
        """
        self.players = [create_player("market", self.pipeline) for _ in range(self.market_size)]

    def reset(self):
        """
        Reset the market to its initial state.
        """
        self.initialize()

    def get_player(self, player_index: int):
        """
        Retrieve a player from the market by ID.
        :param player_index: Index of the player to retrieve.
        :return: Player instance or None if not found.
        """
        return self.players[player_index]

    def remove_player(self, player_index: int):
        """
        Remove a player from the market.
        :param player: The Player instance to remove.
        """
        self.players[player_index] = create_player("empty", self.pipeline)

    def get_players(self, return_none=False):
        """
        Get all players currently in the market.
        :return: List of Player objects.
        """
        if return_none:
            return [player if player.player_type != "empty" else None for player in self.players]
        else:
            return self.players
    
    def refresh(self):
        """
        Refresh the market by replacing some players with new ones.
        Useful for simulating new players entering the market every week.
        """
        num_to_replace = random.randint(1, len(self.players) // 3)  # Replace ~1/3 of the market
        for _ in range(num_to_replace):
            player_to_remove = random.randint(0, len(self.players) - 1)
            self.players[player_to_remove] = create_player("market", self.pipeline)