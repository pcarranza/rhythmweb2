
from serve.page.base import BasePage
from player import PlayerPanel
from status import StatusPanel
from queue import QueuePanel

import socket


class Page(BasePage):
    
    def __init__(self):
        super(BasePage, self).__init__(__file__)
    
    
    def name(self):
        return 'HomePage'

    
    def render_template(self, node):
        self.debug('Rendering template %s' % self.name())
        path = self._environ['PATH_INFO']
        host = socket.gethostname()
        node.title.content = 'Rhythmbox Server - %s - %s' % (host, path)
        node.status.raw = StatusPanel().render()
        node.player.raw = PlayerPanel().render()
        node.queue.raw = QueuePanel().render()
        
        
    def post(self):
        pass