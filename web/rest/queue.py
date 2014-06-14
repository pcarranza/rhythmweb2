from web.rest import RBRest
from rhythmweb.controller import Queue

class Page(RBRest):
    
    def get(self):
        return Queue().get_queue()
