from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from web.rest import Song
from serve.rest.json import JSon

class Page(BaseRest, Loggable):
    
    
    def get(self):
        handler = self._components['RB']
        
        playlist_ids = handler.get_play_queue()
        entries = []
        for entry_id in playlist_ids:
            entry = Song.get_song_as_JSon(handler, entry_id)
            entries.append(entry)
            
        playlist = JSon('playlist')
        playlist.put('entries', entries)
        
        return playlist
