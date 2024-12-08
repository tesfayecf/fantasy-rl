from .BaseService import BaseService

class MarketService(BaseService):
    
    def __init__(self, app):
        super().__init__(app, app.fileManager)

    def _getInitialData(self):
        pass

    

