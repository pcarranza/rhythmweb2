# -*- coding: utf-8 -
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
from serve.rest import JSon
from serve.request import ServerException

import logging
log = logging.getLogger(__name__)

class Page(RBRest):
    
    def get(self):
        handler = self.get_rb_handler()
        
        if not self.has_path_parameters():
            rbplaylists = handler.get_playlists()
            if rbplaylists is None:
                raise ServerException(404, 'No playlists')

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
            
            log.debug('Loading playlist with id %d' % playlist_id)
            playlist = self.get_playlist_by_id(playlist_id) 
            
            if playlist is None:
                raise ServerException(404, 'No playlists')
            
            return self.get_source_as_json(playlist)
            
    
    def post(self):
        action = self.get_parameter('action', True)

        if self.has_parameter('playlist'):
            source_id = self.get_parameter('playlist', True)
        elif self.has_parameter('source'):
            source_id = self.get_parameter('source', True)
        else:
            raise ServerException(400, 'Bad request, no "source" parameter')

        source_id = int(source_id)
        handler = self.get_rb_handler()
        
        if not action:
            raise ServerException(400, 'Bad request, no "action" parameter')

        json = JSon()

        playlist = self.get_playlist_by_id(source_id) 
        if not playlist:
            raise ServerException(400, 'Bad request, there is no playlist with id %d', source_id)

        if action == 'enqueue':
            count = handler.enqueue_source(playlist)
            json.put('count', count)
            if count > 0:
                json.put('result', 'OK')
                
        elif action == 'play_source':
            if handler.play_source(playlist):
                json.put('result', 'OK')
            else:
                json.put('result', 'BAD')
            
        return json

    def get_playlist_by_id(self, playlist_id):
        handler = self.get_rb_handler()
        playlists = handler.get_playlists()
        if len(playlists) < playlist_id:
            raise ServerException(400, 'There is no playlist with id %d' % playlist_id)

        return playlists[playlist_id]


    def get_source_entries(self, source, limit):
        entry_ids = self.get_rb_handler().get_source_entries(source, limit)
        return self.get_songs_as_json_list(entry_ids)
