from web.rest import RBRest
from rhythmweb.model import get_song
from collections import defaultdict

class Page(RBRest):
    
    def get(self):
        handler = self.get_rb_handler()
        entries = handler.get_play_queue()
        queue = defaultdict(lambda:[])
        for entry in entries:
            queue['entries'].append(get_song(entry))
        return queue
