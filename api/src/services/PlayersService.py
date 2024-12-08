import json
import numpy as np
import scipy.stats as stats

from .BaseService import BaseService

class PlayersService(BaseService):
    players = {}

    def __init__(self, app):
        super().__init__(app, app.fileManager)

    def _getInitialData(self):
        """
        This method loads player data from 'common/players.json'.

        Raises:
            Exception: If 'common/players.json' file is not found.
        """
        try:
            with open('api/common/static/players.json') as f:
                self.players = json.load(f)
        except Exception as e:
            raise Exception("No players.json file found")

    # STATIC STATS
    def getInfo(self, player_id):
        """
        Get information about a player by player ID.

        Args:
            player_id (str): The unique identifier of the player.

        Returns:
            dict: Player information as a dictionary.
                Returns None if the player is not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            info = self.players[str(player_id)]
            if not info:
                raise Exception("Player not found")
            return info
        except Exception as e:
            # print(f'PlayersService::getPlayerInfo : {str(e)}')
            return None
    
    def getPlayersIds(self):
        """
        Get a list of player IDs.

        Returns:
            list: A list of player IDs.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            return list(self.players.keys())
        except Exception as e:
            # print(f'PlayersService::getPlayersIds : {str(e)}')
            return None

    def didPlayerPlay(self, player_id, weekId):
        """
        Check if a player played in a specific week.

        Args:
            player_id (str): The unique identifier of the player.
            weekId (int): The week number.

        Returns:
            bool: True if the player played in the week, False otherwise.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            player_stats = self.getStats(player_id)['playerStats']
            if player_stats:
                for stat in player_stats:
                    if stat.get('weekNumber') == weekId:
                        return True
            return False
        except Exception as e:
            # print(f'PlayersService::didPlayerPlay : {str(e)}')
            return None

    # BASIC STATS
    def getStats(self, player_id):
        """
        Get player statistics for a specific player by player ID.

        Args:
            player_id (str): The unique identifier of the player.

        Returns:
            dict: Player statistics as a dictionary.
                Returns None if the player is not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            # Check if the player exists
            if not self.players[str(player_id)]:
                raise Exception("Player not found: " + str(player_id))
            
            # Get file information and read player statistics
            meta, file_path = self.getFileInfo(player_id, "player_stats")
            stats = self.fileManager.read(file_path, meta)
            return stats
        except Exception as e:
            # print(f'PlayersService::getStats : {str(e)}')
            return None

    def getStatsForWeek(self, player_id, week_id):
        """
        Get the statistics of a player for a specific week.

        Args:
            player_id (str): The unique identifier of the player.
            week_id (int): The week number for which statistics are needed.

        Returns:
            dict: Player statistics for the specified week as a dictionary.
                Returns None if the player is not found or if statistics for the week are not available.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            if not self.checkWeekId(week_id):
                raise Exception("Week not found")
            
            player_stats = self.getStats(player_id)["playerStats"]
            if player_stats:
                for stat in player_stats:
                    if stat.get('weekNumber') == week_id:
                        return stat
            return None
        except Exception as e:
            # print(f'PlayersService::getStatsForWeek : {str(e)}')
            return None
    
    # AGGREGATE STATS
    def getBaseAggregate(self, player_id, week_id, stat_name):
        """
        Calculate the total number of a stat for specific player until a specified week or throughout the season.

        Args:
            player_id (str): The unique identifier of the player.
            week_id (int): The week number until which goals are to be calculated.
                If None, it calculates goals for the entire season.
            stat_name (str): Name of the specific stat

        Returns:
            int: Total number of goals scored by the player until the specified week or throughout the season.
            Returns 0 if the player is not found or stat not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            if not self.checkWeekId(week_id):
                raise Exception("Week not found")
            
            if stat_name == 'points': 
                return self.getTotalPoints(player_id, week_id)
            elif stat_name == 'games_played':
                return self.getTotalGamesPlayed(player_id, week_id)
            player_stats = self.getStats(player_id)['playerStats']
            if player_stats:
                if week_id is not None:
                    player_stats = [stat for stat in player_stats if stat.get('weekNumber') <= week_id]
                total = 0
                for stat in player_stats:
                    if stat.get('stats', {}).get(stat_name) == None:
                        continue
                    item = stat.get('stats', {}).get(stat_name, [0, 0])[0]
                    total += item
                return total
            return 0
        except Exception as e:
            # print(f'PlayersService::getBaseAggregate::{stat_name}: {str(e)}')
            return 0

    def getTotalMinutesPlayed(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'mins_played')

    def getTotalGoals(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'goals')

    def getTotalAssists(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'goal_assist')

    def getTotalOfftargetAttemptsAssist(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'offtarget_att_assist')

    def getTotalPenaltyAreaEntries(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'pen_area_entries')

    def getTotalPenaltiesWon(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'penalty_won')

    def getTotalPenaltiesSaved(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'penalty_save')

    def getTotalSaves(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'saves')

    def getTotalEffectiveClearances(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'effective_clearance')

    def getTotalPenaltiesFailed(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'penalty_failed')

    def getTotalOwnGoals(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'own_goals')

    def getTotalGoalsConceded(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'goals_conceded')

    def getTotalYellowCards(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'yellow_card')

    def getTotalSecondYellowCards(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'second_yellow_card')

    def getTotalRedCards(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'red_card')

    def getTotalTotalScoringAttempts(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'total_scoring_att')

    def getTotalWonContests(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'won_contest')

    def getTotalBallRecovery(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'ball_recovery')

    def getTotalPossessionLostAll(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'poss_lost_all')

    def getTotalPenaltiesConceded(self, player_id, week_id=None):
        return self.getBaseAggregate(player_id, week_id, 'penalty_conceded')

    ####
    
    def getTotalPoints(self, player_id, week_id=None):
        """
        Get the total points earned by a specific player until a specified week or throughout the season.

        Args:
            player_id (str): The unique identifier of the player.
            week_id (int): The week number until which points are to be calculated.
                If None, it calculates points for the entire season.

        Returns:
            int: Total points earned by the player until the specified week or throughout the season.
                Returns None if the player is not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            player_stats = self.getStats(player_id)['playerStats']
            if player_stats:
                if week_id is not None:
                    player_stats = [stat for stat in player_stats if stat.get('weekNumber') <= week_id]
                total_points = sum(stat.get('totalPoints', 0) for stat in player_stats)
                return total_points
            return None
        except Exception as e:
            # print(f'PlayersService::getTotalPoints : {str(e)}')
            return None

    def getTotalGamesPlayed(self, player_id, week_id=None):
        """
        Calculate the total number of games played by a player until a specified week or throughout the season.

        Args:
            player_id (str): The unique identifier of the player.
            week_id (int): The week number until which games played are to be calculated.
                If None, it calculates games played for the entire season.

        Returns:
            int: Total number of games played by the player until the specified week or throughout the season.
                Returns 0 if the player is not found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            player_stats = self.getStats(player_id)['playerStats']
            if player_stats:
                if week_id is not None:
                    player_stats = [stat for stat in player_stats if stat.get('weekNumber') <= week_id]
                try:
                    player_stats = [stat for stat in player_stats if stat.get('stats', {}).get('mins_played', 0)[0] > 0]
                except:
                    return 0
                total_games_played = len(player_stats)
                return total_games_played
            return 0
        except Exception as e:
            # print(f'PlayersService::getTotalGamesPlayed : {str(e)}')
            return 0

    def getTotalGoalsParticipation(self, player_id, week_id=None):
        """
        Calculate the percentage of goals for which a player was directly involved, either by scoring or providing an assist.

        Args:
            player_id (str): The unique identifier of the player.
            week_id (int): The week number until which goal participation is to be calculated.
                If None, it calculates goal participation for the entire season.

        Returns:
            float: Goal participation rate as a percentage. Returns None if the player is not found or if no goal participation is available.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            total_goals_scored = self.getTotalGoals(player_id, week_id)
            total_assists = self.getTotalAssists(player_id, week_id)
            if total_goals_scored is not None and total_assists is not None and (total_goals_scored + total_assists) > 0:
                goal_participation = (total_goals_scored / (total_goals_scored + total_assists)) * 100
                return goal_participation
            return 0
        except Exception as e:
            # print(f'PlayersService::getTotalGoalParticipation : {str(e)}')
            return 0

    # ADVANCED STATS
    def getMarketValue(self, player_id):
        try:
            player = self.getStats(player_id)
            if player:
                return player.get('marketValue')
        except Exception as e:
            # print(f'PlayersService::getMarketValue : {str(e)}')
            return 0

    def getMarketValueTrends(self, player_id):
        """
        Analyze how a player's market value changes over the season.

        Args:
            player_id (str): The unique identifier of the player.

        Returns:
            dict: A dictionary containing market value trends over the season.
                Returns None if the player is not found or if market value data is insufficient.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            player_stats = self.getStats(player_id)
            if player_stats:
                # Extract weeks and corresponding market values
                weeks = [stat.get('weekNumber') for stat in player_stats]
                market_values = [stat.get('marketValue') for stat in player_stats]

                # Check if there is sufficient data for analysis
                if len(weeks) > 1 and len(market_values) > 1:
                    # Calculate trend line using linear regression
                    coefficients = np.polyfit(weeks, market_values, 1)
                    polynomial = np.poly1d(coefficients)
                    trend_values = polynomial(weeks)

                    # Return a dictionary containing market value trends
                    return {
                        "weeks": weeks,
                        "market_values": market_values,
                        "trend_values": trend_values.tolist()
                    }
            return None
        except Exception as e:
            print(f'PlayersService::getMarketValueTrends : {str(e)}')
            return None

    def getTTestMinutesPlayed(self, player_id):
        try:
            player_stats = self.getStats(player_id)['playerStats']
            if player_stats:
                minutes_played = [sum(stat.get('stats', {}).get('mins_played', [0, 0])) for stat in player_stats]
                t_test_minutes_played = stats.ttest_1samp(minutes_played, popmean=np.mean(minutes_played))
                return t_test_minutes_played
            return None
        except Exception as e:
            print(f'PlayersService::analyzePlayerStatistics : {str(e)}')
            return None
    
    # OTHER 
    def getAbsences(self):
        """
        Get the list of absences for all players.

        Returns:
            list: A list of absences for all players.
                Returns None if no absences are found.

        Raises:
            Exception: If an error occurs during the data retrieval.
        """
        try:
            # Get file information and read absences
            meta, file_path = self.getFileInfo("", "absences")
            absences = self.fileManager.read(file_path, meta)
            return absences
        except Exception as e:
            print(f'PlayersService::getAbsences : {str(e)}')
            return None
