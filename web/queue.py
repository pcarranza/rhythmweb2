
from serve.page.base import BasePanel
from RhythmWeb import RhythmWeb

class QueuePanel(BasePanel):
    
    def __init__(self):
        super(BasePanel, self).__init__(__file__)
        
    def name(self):
        return 'Queue'
    
    def render_template(self, node):
        handler = RhythmWeb.handler_instance()
        entries = handler.get_play_queue()
        node.row.repeat(self.render_table, entries)
        
        
    def render_table(self, node, entry_id):
        handler = RhythmWeb.handler_instance()

        artist = '[N/A]'
        album = '[N/A]'
        title = '[N/A]'
        track = '[N/A]'
        
        if not entry_id is None:
            entry = handler.load_entry(entry_id)
            if not entry is None:
                artist = entry.artist
                album = entry.album
                title = entry.title
                track = str(entry.track_number)
        
        node.artist.content = artist
        node.album.content = album
        node.title.content = title
        node.track.content = track
        