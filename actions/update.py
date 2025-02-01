from api import API 
from tqdm import tqdm

api = API()
api.init()

weeks = api.teams.getWeekIds()
for week in tqdm(weeks, desc="weeks"):
    matches = api.teams.getWeekMatches(week)
    for match in tqdm(matches, desc="matches"):
        teams = [match["local"]["id"], match["visitor"]["id"]]
        for team_id in tqdm(teams, desc="teams"):
            players = api.teams.getPlayers(team_id)
            for player in tqdm(players, desc="players"):
                player_id = player["id"]
                try:
                    stats = api.players.getStats(player_id)
                except Exception as e:
                    raise Exception(f"Error getting player {player_id} info: {e}")