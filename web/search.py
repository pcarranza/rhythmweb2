

from serve.page.base import BasePanel
from RhythmWeb import RhythmWeb

class SearchPanel(BasePanel):
    
    def __init__(self):
        super(BasePanel, self).__init__(__file__)
        
        
    def name(self):
        return 'Search'
    
    
    def render_template(self, node):
        pass