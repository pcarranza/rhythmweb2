
from serve.page.base import BasePanel
from RhythmWeb import RhythmWeb

class StatusPanel(BasePanel):
    
    def __init__(self):
        super(BasePanel, self).__init__(__file__)
        
        
    def name(self):
        return 'Status'
    
    
    def render_template(self, node):
        handler = RhythmWeb.handler_instance()
        bstatus = handler.get_playing_status()
        
        status = "Paused"
        artist = "[N/A]"
        album = "[N/A]"
        title = "[N/A]"
        time = "[N/A]"

        if bstatus:
            status = "Playing"
            
        pentry = handler.get_playing_entry_id()
        if not pentry is None:
            entry = handler.load_entry(pentry)
            
            artist = entry.artist
            album = entry.album
            title = entry.title
            time = handler.get_time_playing_string()
        
        node.status.content = status
        node.artist.content = artist
        node.album.content = album
        node.title.content = title
        node.time.content = time
        