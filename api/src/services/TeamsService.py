import json
from .BaseService import BaseService

class TeamsService(BaseService):
    teams = {}

    def __init__(self, app):
        super().__init__(app, app.fileManager)

    def _getInitialData(self):
        """
        This constructor loads teams data from 'common/teams.json'.

        Raises:
            Exception: If 'common/teams.json' file is not found.
        """
        try:
            with open('api/common/static/teams.json') as f:
                self.teams = json.load(f)
        except Exception as e:
            raise Exception("No teams.json file found")

    # STATIC STATS
    def getInfo(self, team_id):
        """
        Get information about a team by team ID.

        Args:
            team_id (str): The unique identifier of the team.

        Returns:
            dict: Team information as a dictionary.
                Returns None if the team is not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            info = self.teams[str(team_id)]
            if not info:
                raise Exception("Team not found")
            return info
        except Exception as e:
            raise Exception("Team not found") from e

    def getTeamsIds(self):
        """
        Get a list of team IDs.

        Returns:
            list: List of team IDs.
        """
        return list(self.teams.keys())

    # BASIC STATS
    def getPlayers(self, team_id):
        """
        Get the players of a team by team ID.

        Args:
            team_id (str): The unique identifier of the team.

        Returns:
            list: List of players for the specified team.
                Returns None if the team or its players are not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            found = self.teams.get(str(team_id))
            if not found:  
                raise Exception("Team not found")

            # Get file information and read team players
            meta, file_path = self.getFileInfo(team_id, "team_players")
            team_players = self.fileManager.read(file_path, meta)

            if "players" in team_players:
                return team_players["players"]
            else:
                raise Exception("No player data found for this team.")
            
        except Exception as e:
            raise Exception("Error while fetching team players.") from e

    def getMatches(self, team_id):
        """
        Get the matches played by a specific team.

        Args:
            team_id (str): The unique identifier of the team.

        Returns:
            list: A list of the matches played by the team.
                Returns an empty list if the team or team matches' data are not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            found = self.teams.get(str(team_id))
            if not found:  
                raise Exception("Team not found")
            
            # Get file information and read team players
            meta, file_path = self.getFileInfo(team_id, "team_matches")
            team_matches = self.fileManager.read(file_path, meta)

            if team_matches:
                return team_matches
            else:
                raise Exception("No match data found for this team.")
            
        except Exception as e:
            raise Exception("Error while fetching team matches.") from e

    def getMatchesPlayed(self, team_id):
        """
        Get the number of matches played by a specific team. (matchState = 7)

        Args:
            team_id (str): The unique identifier of the team.

        Returns:
            int: The number of matches played by the team.
                Returns 0 if the team or team matches' data are not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            matches = self.getMatches(team_id)
            return [stat for stat in matches if stat.get('matchState') <= 7]
        except Exception as e:
            raise Exception("Error while fetching matches played.") from e
            
    def getIdealTeam(self, week_id):
        """
        Get the ideal team for a specific week.

        Args:
            week_id (str): The unique identifier of the week.

        Returns:
            dict: Information about the ideal team for the week.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            week_ids = self.getWeekIds()
            if not week_id in week_ids:
                raise Exception("Week not found")
            
            meta, file_path = self.getFileInfo(week_id, "ideal_team")
            ideal_team = self.fileManager.read(file_path, meta)
            if ideal_team:
                return ideal_team
            else:
                raise Exception("No ideal team found for this week.")
        except Exception as e:
            raise Exception("Error while fetching ideal team.") from e
    
    def getMostProfitableTeam(self, week_id):
        """
        Get the profitable team for a specific team.

        Args:
            week_id (str): The unique identifier of the week.

        Returns:
            dict: Information about the profitable team for the week.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            week_ids = self.getWeekIds()
            if not week_id in week_ids:
                raise Exception("Week not found")

            meta, file_path = self.getFileInfo(week_id, "profitable_team")
            profitable_team = self.fileManager.read(file_path, meta)
            if profitable_team:
                return profitable_team
            else:
                raise Exception("No profitable team found for this team.")
        except Exception as e:
            raise Exception("Error while fetching profitable team.") from e
    
    # AGGREGATE STATS 
    def getBaseAggregate(self, team_id, week_id, stat_name):
        """
        Calculate the total number of a stat for specific team until a specified week or throughout the season.

        Args:
            team_id (str): The unique identifier of the team.
            week_id (int): The week number until which goals are to be calculated.
                If None, it calculates goals for the entire season.
            stat_name (str): Name of the specific stat

        Returns:
            int: Total number of a specific stat by the player until the specified week or throughout the season.
            Returns 0 if the team is not found or stat not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            if not self.checkWeekId(week_id):
                raise Exception("Week not found")
            
            players = self.getPlayers(team_id)

            if not players:
                raise Exception("Team not found")

            total = 0
            for player in players:
                player_id = player.get('id')
                if not player_id:
                     raise Exception("Error getting player id")
                player_total = self.app.players.getBaseAggregate(player_id, week_id, stat_name)
                total += player_total
            return total
        except Exception as e:
            print(f'PlayersService::getBaseAggregate::{stat_name}: {str(e)}')
            return 0

    def getTotalGoals(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'goals')

    def getTotalAssists(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'goal_assist')

    def getTotalOfftargetAttemptsAssist(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'offtarget_att_assist')

    def getTotalPenaltyAreaEntries(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'pen_area_entries')

    def getTotalPenaltiesWon(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'penalty_won')

    def getTotalPenaltiesSaved(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'penalty_save')

    def getTotalSaves(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'saves')

    def getTotalEffectiveClearances(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'effective_clearance')

    def getTotalPenaltiesFailed(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'penalty_failed')

    def getTotalOwnGoals(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'own_goals')

    def getTotalGoalsConceded(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'goals_conceded')

    def getTotalYellowCards(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'yellow_card')

    def getTotalSecondYellowCards(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'second_yellow_card')

    def getTotalRedCards(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'red_card')

    def getTotalTotalScoringAttempts(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'total_scoring_att')

    def getTotalWonContests(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'won_contest')

    def getTotalBallRecovery(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'ball_recovery')

    def getTotalPossessionLostAll(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'poss_lost_all')

    def getTotalPenaltiesConceded(self, team_id, week_id=None):
        return self.getBaseAggregate(team_id, week_id, 'penalty_conceded')

    ###

    def getTotalMarketValue(self, teamId):
        """
        Get the total market value of a specific team throughout the season.

        Args:
            teamId (str): The unique identifier of the team.

        Returns:
            int: Total market value of the team throughout the season.
                Returns None if the team or team players' data are not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            players = self.getPlayers(teamId)
            if players:
               raise Exception("Team not found")
            
            total = 0
            for player in players:
                player_id = player.get('id')
                if not player_id:
                    raise Exception("Error getting player id")
                total += self.app.players.getMarketValue(player_id)
            return total
        except Exception as e:
            print(f'TeamsService::getTotalMarketValue: {str(e)}')
            return 0

    # def getTotalGoals(self, team_id, week_id=None):
    #     """
    #     Calculate the total number of goals scored by a specific team up to a specified week or throughout the season.

    #     Args:
    #         team_id (str): The unique identifier of the team.
    #         week_id (int, optional): The week number until which goals are to be calculated.
    #             If None, it calculates goals for the entire season.

    #     Returns:
    #         int: Total number of goals scored by the team until the specified week or throughout the season.
    #             Returns 0 if the team is not found or if no goals are scored.

    #     Raises:
    #         Exception: If an error occurs during data retrieval.
    #     """
    #     try:
    #         found = self.teams.get(str(team_id))
    #         if not found:
    #             raise Exception("Team not found")

    #         # TODO: filter matches by week
    #         team_matches = self.getMatches(team_id)
    #         if team_matches:
    #             goals = 0
    #             for match in team_matches:
    #                 if match['local']['id'] == team_id:
    #                     if match['local_score'] is not None:
    #                         goals += match['local_score']
    #                 else:
    #                     if match['visitor_score'] is not None:
    #                         goals += match['visitor_score']
    #             return goals
    #         return 0
    #     except Exception as e:
    #         print(f'TeamsService::getTotalGoals: {str(e)}')
    #         return 0

    def getTotalGoalsAgainst(self, team_id, week_id=None):
        """
        Calculate the total number of goals conceded by a specific team up to a specified week or throughout the season.

        Args:
            team_id (str): The unique identifier of the team.
            week_id (int, optional): The week number until which goals are to be calculated.
                If None, it calculates goals for the entire season.

        Returns:
            int: Total number of goals conceded by the team until the specified week or throughout the season.
                Returns 0 if the team is not found or if no goals are conceded.

        Raises:
            Exception: If an error occurs during data retrieval.
        """
        try:
            found = self.teams.get(str(team_id))
            if not found:
                raise Exception("Team not found")

            team_matches = self.getMatches(team_id, week_id)
            if team_matches:
                goals_conceded = 0
                for match in team_matches:
                    if match['local']['id'] == team_id:
                        if match['visitor_score'] is not None:
                            goals_conceded += match['visitor_score']
                    else:
                        if match['local_score'] is not None:
                            goals_conceded += match['local_score']
                return goals_conceded
            return 0
        except Exception as e:
            print(f'TeamsService::getTotalGoalsAgainst: {str(e)}')
            return 0
     
    def getTotalPoints(self, team_id, week_id=None):
        """
        Get the total points earned by a specific team up to a specified week or throughout the season.

        Args:
            team_id (str): The unique identifier of the team.
            week_id (int, optional): The week number until which points are to be calculated.
                If None, it calculates points for the entire season.

        Returns:
            int: Total points earned by the team until the specified week or throughout the season.
                Returns 0 if the team is not found or if no points are earned.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            found = self.teams.get(str(team_id))
            if not found:
                raise Exception("Team not found")

            team_players = self.getPlayers(team_id)
            total_points = 0
            if team_players:
                for player in team_players:
                    if "playerStats" in player:
                        player_stats = player["playerStats"]
                        if week_id is not None:
                            player_stats = [stat for stat in player_stats if stat.get('weekNumber') <= week_id]
                        total_points += sum(stat.get("totalPoints", 0) for stat in player_stats)
            return total_points
        except Exception as e:
            print(f'TeamsService::getTotalPoints: {str(e)}')
            return 0
