import random

from .player import Player
from pipeline import Pipeline

def create_player(type: str, pipeline: Pipeline):
    player_id = random.randint(1, 100000)
    player_data, next_week_points = pipeline.get_player()

    if type == "team":
        release_clause = player_data.get('market_value', 0) + random(100000, 10000000)
        player = Player(
            player_id=player_id, 
            metrics=list(player_data.values()), 
            type=type,
            release_clause=release_clause,
            points=next_week_points
        )
    elif type == "market":
        release_clause = player_data.get('market_value', 0)
        player = Player(
            player_id=player_id,
            metrics=list(player_data.values()),
            type=type,
            release_clause=release_clause,
            points=next_week_points
        )

    return player

