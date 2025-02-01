from environment.factory import create_player

class Team:
    """
    Represents a fantasy football team.

    Attributes:
        team_size (int): The number of players on the team.
        pipeline (Pipeline): The data pipeline for getting player data.
        players (list): The list of players on the team.
    """
    def __init__(self, team_size, pipeline):
        self.team_size = team_size
        self.pipeline = pipeline
        self.players = []

        self.initialize()

    def initialize(self):
        """
        Initialize the team with a random set of players.
        """
        self.players = [create_player('team', self.pipeline) for _ in range(self.team_size)]
    
    def reset(self):
        """
        Reset the team to its initial state.
        """
        self.initialize()
    
    def get_player(self, player_index):
        """
        Get a player from the team by index.

        Args:
            player_index (int): The index of the player to get.

        Returns:
            Player: The player at the given index.
        """
        return self.players[player_index]
    
    def add_player(self, player):
        """
        Add a player to the team.

        Args:
            player (Player): The player to add.
        """
        # Find empty slot and add player
        for i, p in enumerate(self.players):
            if p.player_type == 'empty':
                self.players[i] = player
                return
    
    def remove_player(self, player_index):
        """
        Remove a player from the team and replace with an "empty" player.

        Args:
            player_index (int): The index of the player to remove.
        """
        self.players[player_index] = create_player('empty', self.pipeline)

    def get_players(self, return_none=False):
        """
        Get the list of players on the team, excluding "empty" players.

        Returns:
            list: The list of players on the team.
        """
        if return_none:
            return [player if player.player_type != "empty" else None for player in self.players]
        else:
            return self.players

    def get_points(self):
        """
        Get the total points of the team.

        Returns:
            int: The total points of the team.
        """
        return sum([player.points for player in self.players])
