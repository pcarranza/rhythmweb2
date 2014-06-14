from web.rest import RBRest
from rhythmweb.controller import Player

class Page(RBRest):
    
    def get(self):
        return Player().status()
