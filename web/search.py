

from serve.page.base import BasePanel

class SearchPanel(BasePanel):
    
    def __init__(self, components):
        super(BasePanel, self).__init__(__file__)
        
        
    def name(self):
        return 'Search'
    
    
    def render_template(self, node):
        pass