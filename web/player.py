
from serve.page.base import BasePanel

class PlayerPanel(BasePanel):
    
    handler = None
    
    def __init__(self, request, handler):
        BasePanel.__init__(self, request, __file__)
        self.handler = handler
    
        
    def name(self):
        return 'Player'
    
    
    def render_template(self, node):
        pass