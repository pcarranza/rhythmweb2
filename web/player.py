
from serve.page.base import BasePanel


class PlayerPanel(BasePanel):
    
    def __init__(self, components):
        super(BasePanel, self).__init__(__file__)
    
    
    def name(self):
        return 'Player_Panel'
    
    
    def render_template(self, node):
        pass