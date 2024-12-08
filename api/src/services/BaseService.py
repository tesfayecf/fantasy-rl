from api.common.utils.ApiConfig import api_config
from ..managers.FileManager import FileManager

class BaseService:
    players = {}
    teams = {}
    market = {}

    def __init__(self, app, fileManager: FileManager):
        self.fileManager = fileManager
        self.app = app
        self._getInitialData()
    
    def getFileInfo(self, id, key):
        meta = self.__get_file_meta(id, key)
        file_path = self.__get_file_path(id, key)
        return meta, file_path
    
    def getAppConfig(self):
        """
        Get the application configuration.

        Returns:
            dict: The application configuration.
        """
        try:
            # Get file information and read team players
            meta, file_path = self.getFileInfo("", "app_config")
            file_config = self.fileManager.read(file_path, meta)
            if file_config:
                return file_config
            else:
                raise Exception("No app config found")
        except Exception as e:
            raise Exception("Error while fetching app config.") from e
    
    # API GENERAL
    def getWeekMatches(self, week_id):
        """
        Get the matches for a specific week.

        Args:
            week_id (int): The week number for which matches are needed.

        Returns:
            list: A list of matches for the specified week.
        """
        try:
            meta, file_path = self.getFileInfo(week_id, "week_matches")
            week_matches = self.fileManager.read(file_path, meta)
            if week_matches:
                return week_matches
            else:
                raise Exception("Week matches not found")
        except Exception as e:
            raise Exception("Error while fetching matches.") from e
    
    def getMatchWeekId(self, match_id):
        """
        Get the week ID for a specific match.

        Args:
            match_id (int): The unique identifier of the match.

        Returns:
            int: The week ID for the specified match.
        """
        try:
            
            week_matches = self.getWeekMatches()
            if week_matches:
                return week_matches[match_id]["week_id"]
            else:
                raise Exception("No app config found")
        except Exception as e:
            raise Exception("Error while fetching week id.") from e

    def getWeekIds(self):
        """
        Get a list of week IDs.

        Returns:
            list: A list of week IDs.
        """
        try:
            week_info = self.getAppConfig()[9]
            return week_info["value"]
        except Exception as e:
            raise Exception("Error while fetching week ids.") from e
        
    def checkWeekId(self, week_id):
        """
        Check if a week ID exists.

        Args:
            week_id (int): The week ID to check.

        Returns:
            bool: True if the week ID exists, False otherwise.
        """
        try:
            week_ids = self.getWeekIds()
            if week_id in week_ids:
                return True
            else:
                return False
        except Exception as e:
            raise Exception("Error while checking week id") from e

    def getCurrentWeekId(self):
        """
        Get the current week ID.

        Returns:
            int: The current week ID.
        """
        try:
            app_config = self.getAppConfig()
            week_info = app_config[9]
            return week_info["value"][-1]
        except Exception as e:
            raise Exception("Error while fetching current week id.") from e

    #######################
    ### PRIVATE METHODS ###
    #######################

    def __get_file_meta(self, id, key):
        return {
            'id': id,
            'name': api_config[key]['base_name'] + str(id),
            "url": api_config[key]['base_url'] + str(id),
            "last_update": 0,
            "update_interval": api_config[key]['update_interval'],
            "fields": api_config[key]['fields']
        }
    
    def __get_file_path(self, id, key):
        return api_config[key]["base_path"] + api_config[key]["base_name"]  + str(id) + ".json"