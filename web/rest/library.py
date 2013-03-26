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
from serve.rest.json import JSon
from serve.request import ServerException

SEARCH_TYPES = {'artists' : 'artist', 'genres' : 'genre', 'albums' : 'album'}

class Page(RBRest):
    
    def get(self):
        if not self.has_path_parameters():
            raise ServerException(400, 'Bad request, no parameters')
       
        search_by = self.get_path_parameter(0)
        
        if not SEARCH_TYPES.has_key(search_by):
            raise ServerException(400, 'Bad request, path parameter "%s" not supported' % search_by)
        
        if self.get_path_parameters_size() == 1:
            library = JSon()
            handler = self.get_rb_handler()
            
            if 'artists' == search_by:
                library.put('artists', self.get_library_as_json_list(handler.get_artists()))
                (name, value) = handler.get_biggest_artist()
                library.put('biggest_artist', self.get_name_value_as_json(name, value))
                
            elif 'genres' == search_by:
                library.put('genres', self.get_library_as_json_list(handler.get_genres()))
                (name, value) = handler.get_biggest_genre()
                library.put('biggest_genre', self.get_name_value_as_json(name, value))
                
            else:
                library.put('albums', self.get_library_as_json_list(handler.get_albums()))
                (name, value) = handler.get_biggest_album()
                library.put('biggest_album', self.get_name_value_as_json(name, value))
                
            return library
        
        else:
            value = self.get_path_parameter(1)
            value = str(value).replace('+', ' ')
            
            filter = {}
            filter['type'] = 'song'
            filter[SEARCH_TYPES[search_by]] = value
            filter['exact-match'] = True
            filter['limit'] = 0
            
            handler = self.get_rb_handler()
            
            entry_ids = handler.query(filter)
            log.info('entry_ids')
            log.info(entry_ids)
            entries = self.get_songs_as_json_list(entry_ids)
            library = JSon()
            library.put(SEARCH_TYPES[search_by], value)
            library.put('entries', entries)
            
            return library


    def get_logname(self):
        return 'LIBRARY'
