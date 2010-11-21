
from web import home

class Page(home.Page):
    
    def __init__(self, request):
        home.Page.__init__(self, request)
        self.handler.prev()
    