
class Player:
    def __init__(self, player_id, metrics, player_type="market", release_clause=0, points=0):
        """
        Initialize a player instance.
        :param player_id: Unique identifier for the player.
        :param stats: Dictionary of player statistics.
        :param release_clause: Initial release clause value. Defaults to 0 (no clause).
        """
        self.player_id = player_id
        self.metrics = metrics
        self.release_clause = release_clause
        self.player_type = player_type
        self.points = points

    def __repr__(self):
        return (
            f"Player({self.player_id}, state={self.player_type}, "
            f"release_clause={self.release_clause})"
        )
