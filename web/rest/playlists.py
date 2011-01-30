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
            rbplaylists = handler.get_sources()
            sources = []
            for source in rbplaylists:
                jsource = self.get_source_as_json(source)
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
            
            playlist = handler.get_source(playlist_id)
            if playlist is None:
                raise ServerException(400, 'Bad request, playlist id %d is not valid' % playlist_id)
            
            limit = 100
            if self.get_path_parameters_size() > 1:
                _limit = self.get_path_parameter(1)
                if str(limit).isdigit():
                    limit = int(_limit)
            
            jplaylist = self.get_source_as_json(playlist, self.get_source_entries(playlist, limit))
            
            return jplaylist
            
    
    def post(self):
        action = self.get_parameter('action', True)
        
        json = JSon()
        
        if action == 'enqueue':
            if self.has_parameter('playlist'):
                source = self.get_parameter('playlist', True)
            elif self.has_parameter('source'):
                source = self.get_parameter('source', True)
            else:
                raise ServerException(400, 'Bad request, no "source" parameter')

            count = self.get_rb_handler().enqueue_source(int(source))
            json.put('count', count)
            if count > 0:
                json.put('result', 'OK')
                
        if action == 'play_source':
            source = self.get_parameter('source', True)
            if self.get_rb_handler().play_source(int(source)):
                json.put('result', 'OK')
            else:
                json.put('result', 'BAD')
            
        return json


    def get_source_entries(self, source, limit):
        entry_ids = self.get_rb_handler().get_source_entries(source, limit)
        return self.get_songs_as_json_list(entry_ids)


    def get_logname(self):
        return 'PLAYLISTS'
