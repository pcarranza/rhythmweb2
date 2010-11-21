
from serve.page.base import BasePage
from rbhandle.handler import RhythmboxHandler
from player import PlayerPanel
from status import StatusPanel

import socket


class Page(BasePage):
    
    handler = RhythmboxHandler()
    
    def __init__(self, request):
        BasePage.__init__(self, request, __file__)
    
    def name(self):
        return 'HomePage'
    
    def render_template(self, node):
        host = socket.gethostname()
        path = self._request.path
        node.title.content = 'Rhythmbox Server - %s - %s' % (host, path)
        node.status.raw = StatusPanel(self._request, self.handler).render()
        node.player.raw = PlayerPanel(self._request, self.handler).render()
        
