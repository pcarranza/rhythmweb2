# Rhythmweb - Rhythmbox web REST + Ajax environment for remote control
# Copyright (C) 2010  Pablo Carranza
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from serve.rest.json import JSon
from web.rest import Song

class Page(BaseRest, Loggable):
    
    
    def get(self):
        handler = self._components['RB']
        
        is_playing = handler.get_playing_status()
        
        status = JSon()
        status.put('playing', is_playing)
        if is_playing:
            playing_entry_id = handler.get_playing_entry_id()
            if playing_entry_id:
                status.put('playing_entry', Song.get_song_as_JSon(handler, playing_entry_id))
                status.put('playing_time', handler.get_playing_time())
            
        status.put('playing_order', handler.get_play_order())
        
        return status
        
