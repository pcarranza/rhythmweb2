
from serve.page.base import BasePanel
from RhythmWeb import RhythmWeb

class QueuePanel(BasePanel):
    
    _entries = None
    
    def __init__(self, entries):
        super(BasePanel, self).__init__(__file__)
        self._entries = entries
    
        
    def name(self):
        return 'Queue'
    
    
    def render_template(self, node):
        node.row.repeat(self.render_table, self._entries)
        
        
    def render_table(self, node, entry_id):
        handler = RhythmWeb.handler_instance()

        artist = '[N/A]'
        album = '[N/A]'
        title = '[N/A]'
        track = '[N/A]'
        duration = '[N/A]'
        
        if not entry_id is None:
            entry = handler.load_entry(entry_id)
            if not entry is None:
                artist = entry.artist
                album = entry.album
                title = entry.title
                track = str(entry.track_number)
                duration = str(entry.duration)
        
        node.song.atts['value'] = str(entry_id)
        node.artist.content = artist
        node.album.content = album
        node.title.content = title
        node.duration.content = duration
        node.track.content = track
        
        