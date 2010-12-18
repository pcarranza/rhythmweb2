
from serve.page.base import BasePanel

class QueuePanel(BasePanel):
    
    _entries = None
    
    def __init__(self, entries, components):
        super(BasePanel, self).__init__(__file__)
        self._entries = entries
        self._handler = components['RB']
    
        
    def name(self):
        return 'Queue'
    
    
    def render_template(self, node):
        node.row.repeat(self.render_table, self._entries)
        
        
    def render_table(self, node, entry_id):
        handler = self._handler
        artist = '[N/A]'
        album = '[N/A]'
        title = '[N/A]'
        track = '[N/A]'
        duration = '[N/A]'
        rating = '-'
        
        if not entry_id is None:
            entry = handler.load_entry(entry_id)
            
            r = lambda x: '*' * x
            if not entry is None:
                artist = entry.artist
                album = entry.album
                title = entry.title
                track = str(entry.track_number)
                duration = self.readable_time(int(entry.duration))
                if not entry.rating is None:
                    rating = int(entry.rating)
                    rating = r(rating)
        
        node.song.atts['value'] = str(entry_id)
        node.artist.content = artist
        node.album.content = album
        node.title.content = title
        node.duration.content = duration
        node.rating.content = rating
        node.track.content = track
        
    def readable_time(self, time):
        minutes = time / 60
        seconds = time % 60
        if minutes > 60:
            hours = minutes / 60
            minutes = minutes % 60
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        
        return "%d:%02d" % (minutes, seconds)