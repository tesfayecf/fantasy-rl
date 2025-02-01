import random
import numpy as np

from .player import Player
from pipeline import Pipeline

def create_player(player_type: str, pipeline: Pipeline):
    player_id = random.randint(1, 100000)
    player_data, next_week_points = pipeline.get_player()

    if player_type == "team":
        release_clause = player_data.get('market_value', 0) + random.randint(100000, 10000000)
        player = Player(
            player_id=player_id, 
            metrics=list(player_data.values()), 
            player_type=player_type,
            release_clause=release_clause,
            points=next_week_points
        )
    elif player_type == "market":
        release_clause = player_data.get('market_value', 0)
        player = Player(
            player_id=player_id,
            metrics=list(player_data.values()),
            player_type=player_type,
            release_clause=release_clause,
            points=next_week_points
        )
    elif player_type == "empty":
        release_clause = 0
        player = Player(
            player_id=-1,
            metrics=list(np.zeros(len(player_data.values()))),
            player_type="empty",
            release_clause=0,
            points=0
        )
    else:
        raise ValueError(f"Invalid player type: {player_type}")

    return player