
class Player:
    def __init__(self, player_id, metrics, type="market", release_clause=0, points=0):
        """
        Initialize a player instance.
        :param player_id: Unique identifier for the player.
        :param stats: Dictionary of player statistics.
        :param release_clause: Initial release clause value. Defaults to 0 (no clause).
        """
        self.player_id = player_id
        self.metrics = metrics
        self.release_clause = release_clause
        self.type = type
        self.points = points

    def buy(self):
        """
        Handle buying the player.
        :param buyer_team: Team purchasing the player.
        :param price: Amount paid for the player.
        :return: Success (True) or failure (False).
        """
        if self.type == "market":
            self.type = "team"
            # print(f"Player {self.player_id} bought by {buyer_team.name} for {price}.")
            return True
        else:
            print(f"Failed to buy player {self.player_id}.")
            return False

    def sell(self):
        """
        Handle selling the player.
        :param buyer_team: Team purchasing the player.
        :param price: Amount received for the player.
        :return: Success (True) or failure (False).
        """
        if self.type == "team":
            self.type = "market"
            # print(f"Player {self.player_id} sold to {buyer_team.name} for {price}.")
            return True
        else:
            print(f"Failed to sell player {self.player_id}.")
            return False

    def change_clause(self, new_clause):
        """
        Update the player's release clause.
        :param new_clause: New release clause value.
        """
        if self.type == "team":
            self.release_clause = new_clause
            print(f"Player {self.player_id}'s release clause set to {new_clause}.")

    def __repr__(self):
        return (
            f"Player({self.player_id}, state={self.type}, "
            f"release_clause={self.release_clause})"
        )
