
from web import home
from RhythmWeb import RhythmWeb

class Page(home.Page):
    
    def __init__(self):
        home.Page.__init__(self)
        handler = RhythmWeb.handler_instance()
        handler.next()
    