from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from serve.rest.json import JSon
from web.rest import Song

class Page(BaseRest, Loggable):
    
    
    def get(self):
        handler = self._components['RB']
        
        is_playing = handler.get_playing_status()
        
        status = JSon('status')
        status.put('playing', is_playing)
        if is_playing:
            playing_entry_id = handler.get_playing_entry_id()
            if playing_entry_id:
                status.put('playing_entry', Song.get_song_as_JSon(handler, playing_entry_id))
                status.put('playing_time', handler.get_playing_time())
            
        status.put('playing_order', handler.get_play_order())
        
        return status
        
