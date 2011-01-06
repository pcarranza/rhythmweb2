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
from web.rest import Song
from serve.rest.json import JSon
from serve.request import ServerException

SEARCH_TYPES = {'artists' : 'artist', 'genres' : 'genre', 'albums' : 'album'}

class Page(BaseRest, Loggable):
    
    def get(self):
        if self._path_params is None:
            raise ServerException(400, 'Bad request, no parameters')
       
        search_by = self.unpack_value(self._path_params[0])
        
        if not SEARCH_TYPES.has_key(search_by):
            raise ServerException(400, 'Bad request, %s path parameter not supported' % search_by)
        
        if len(self._path_params) == 1:
            library = JSon()
            handler = self._components['RB']
            
            if 'artists' == search_by:
                library.put('artists', handler.get_artists())
                library.put('biggest_artist', handler.get_biggest_artist())
                
            elif 'genres' == search_by:
                library.put('genres', handler.get_genres())
                library.put('biggest_genre', handler.get_biggest_genre())
                
            else:
                library.put('albums', handler.get_albums())
                library.put('biggest_album', handler.get_biggest_album())
                
            return library
        
        else:
            value = self.unpack_value(self._path_params[1])
            value = str(value).replace('+', ' ')
            
            filter = {}
            filter['type'] = 'song'
            filter[SEARCH_TYPES[search_by]] = value
            filter['exact-match'] = True
            filter['limit'] = 0
            
            handler = self._components['RB']
            
            entry_ids = handler.query(filter)
            entries = []
            for entry_id in entry_ids:
                entry = Song.get_song_as_JSon(handler, entry_id)
                entries.append(entry)
                
            library = JSon()
            library.put(search_by, value)
            library.put('entries', entries)
            
            return library
