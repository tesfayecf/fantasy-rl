from api.src.services.BaseService import BaseService
from api.src.services.PlayersService import PlayersService
from api.src.services.TeamsService import TeamsService
from api.src.services.MarketService import MarketService

from api.src.managers.RequestManager import RequestManager
from api.src.managers.FileManager import FileManager

class API:
    """
    Fantasy API
    """
    requestManager = None
    fileManager = None

    players = None
    teams = None
    market = None

    def __init__(self):
        self.requestManager = RequestManager()
        self.fileManager = FileManager(self.requestManager)

    def config(self, requestConfig, fileConfig):
        self.setRequestConfig(requestConfig)
        self.setFileConfig(fileConfig)

    def init(self):
        self.players = PlayersService(self)
        self.teams = TeamsService(self)
        self.market = MarketService(self)
