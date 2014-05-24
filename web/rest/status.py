from web.rest import RBRest
from rhythmweb.model import get_status

class Page(RBRest):
    
    def get(self):
        return get_status(self.get_rb_handler())
