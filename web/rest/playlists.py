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

from web.rest import RBRest
from serve.rest.json import JSon
from serve.request import ServerException

class Page(RBRest):
    
    def get(self):
        handler = self.get_rb_handler()
        
        if not self.has_path_parameters():
            rbplaylists = handler.get_playlists()
            sources = []
            for source in rbplaylists:
                jsource = self.get_playlist_as_json(source)
                sources.append(jsource)
                
            playlists = JSon()
            playlists.put('playlists', sources)
            
            return playlists
        
        else:
            playlist_id = self.get_path_parameter(0)
            if not playlist_id.isdigit():
                raise ServerException(400, 'Bad request, path parameter must be an int')

            playlist_id = int(playlist_id)
            
            self.trace('Loading playlist with id %d' % playlist_id)
            
            playlist = handler.get_playlist(playlist_id)
            if playlist is None:
                raise ServerException(400, 'Bad request, playlist id %d is not valid' % playlist_id)
            
            jplaylist = self.get_playlist_as_json(playlist, self.get_playlist_entries(playlist_id))
            
            return jplaylist
            
    
    def post(self):
        action = self.get_parameter('action', True)
        
        json = JSon()
        
        if action == 'enqueue':
            playlist = self.get_parameter('playlist', True)
            count = self.get_rb_handler().enqueue_playlist(int(playlist))
            json.put('count', count)
            if count > 0:
                json.put('result', 'OK')
            
        return json


    def get_playlist_entries(self, id):
        entry_ids = self.get_rb_handler().get_playlist_entries(id)
        return self.get_songs_as_json_list(entry_ids)


    def get_logname(self):
        return 'PLAYLISTS'
