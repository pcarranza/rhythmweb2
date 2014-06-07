from web.rest import RBRest
from rhythmweb.controller import Queue

class Page(RBRest):
    
    def get(self):
        return Queue(self.get_rb_handler()).get_queue()
