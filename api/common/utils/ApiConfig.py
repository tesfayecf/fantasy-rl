# Ideal team reward
# https://api-fantasy.llt-services.com/api/v4/team/12011106/rewards/collect-all?rewardType=idealFormationReward&x-lang=es


api_config = {
    # PLAYERS
    "player_stats": {
        "base_name": "player_stats_",
        "base_url": "https://api-fantasy.llt-services.com/api/v3/player/",
        "update_interval": 60*60*24,
        "fields": ["averagePoints", "marketValue", "playerStatus", "points", "playerStats"],
        "base_path": "api/data/player_stats/"
    },

    # TEAMS
    "team_players": {
        "base_name": "team_players_",
        "base_url": "https://api-fantasy.llt-services.com/api/v3/player/team/",
        "update_interval": 60*60*24,
        "fields": ["id", "slug", "players"],
        "base_path": "api/data/team_players/"
    },

    "team_matches": {
        "base_name": "team_matches_",
        "base_url": "https://api-fantasy.llt-services.com/api/v3/calendar/team/",
        "update_interval": 60*60*24,
        "fields": ["id", "date", "featured", "localScore", "matchState", "visitorScore", "local", "visitor"],
        "base_path": "api/data/team_matches/"
    },

    "ideal_team": {
        "base_name": "ideal_team_",
        "base_url": "https://api-fantasy.llt-services.com/api/v4/ideal/",
        "update_interval": 60*60*24,
        "fields": ["formation", "teamValue"],
        "base_path": "api/data/ideal_team/"
    },

    "profitable_team": {
        "base_name": "profitable_team_",
        "base_url": "https://api-fantasy.llt-services.com/api/v4/profitable/",
        "update_interval": 60*60*24,
        "fields": ["formation", "teamValue"],
        "base_path": "api/data/profitable_team/"
    },

    # OTHERS
    "app_config": {
        "base_name": "app_config",
        "base_url": "https://api-fantasy.llt-services.com/app/config/",
        "update_interval": 60*60*24,
        "fields": ["active", "name", "value"],
        "base_path": "api/data/app_config/"
   },

   "week_matches": {
       "base_name": "week_matches_",
       "base_url": "https://api-fantasy.llt-services.com/stats/v1/stats/week/",
       "update_interval": 60*60*24,
       "fields": ["id", "date", "localScore", "matchState", "visitorScore", "local", "visitor"],
       "base_path": "api/data/week_matches/"
   },

    "absences": {
        "base_name": "absences",
        "base_url": "https://api-fantasy.llt-services.com/stats/v1/players/status",
        "update_interval": 60*60*24,
        "fields": ["id", "slug", "players"],
        "base_path": "api/data/absences/"
    },
}