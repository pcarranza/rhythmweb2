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
from serve.request import ServerException
from web.rest import Song

class Page(BaseRest, Loggable):
    
    
    def get_song_id(self):
        if not self._path_params:
            return None
        
        params = self._path_params
        
        if len(params) != 1:
            raise ServerException(400, 'Bad Request')
        
        song_id = int(params[0])
        
        self.debug('Song %d' % song_id)
        
        return song_id
    
    
    
    def get(self):
        song_id = self.get_song_id()
        
        if song_id is None:
            return None
        
        handler = self._components['RB']
        
        return Song.get_song_as_JSon(handler, song_id)
        
        
    def post(self):
        song_id = self.get_song_id()
        
        if song_id is None:
            return None

        params = self._parameters
        handler = self._components['RB']
        
        if 'rating' in params:
            rating = self.unpack_value(params['rating'])
            self.debug('Rating %s' % rating)
            handler.set_rating(song_id, int(rating))
        
        return self.get()
        
        
    def not_found(self):
        return 'Song not found :('
    
    
    

