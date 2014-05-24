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
from serve.request import ServerException
from rhythmweb.model import get_song
from collections import defaultdict

SEARCH_TYPES = {'artists' : 'artist', 'genres' : 'genre', 'albums' : 'album'}

class Page(RBRest):
    
    def get(self):
        if not self.has_path_parameters():
            raise ServerException(400, 'Bad request, no parameters')

        search_by = self.get_path_parameter(0)
        if search_by not in SEARCH_TYPES:
            raise ServerException(400, 'Bad request, path parameter "%s" not supported' % search_by)
        
        library = defaultdict(lambda:[])
        if self.get_path_parameters_size() == 1:
            raise ServerException(400, 'path params by type only search is not supported now')
        else:
            value = self.get_path_parameter(1)
            value = str(value).replace('+', ' ')
            
            query = {}
            query['type'] = 'song'
            query[SEARCH_TYPES[search_by]] = value
            query['exact-match'] = True
            query['limit'] = 0
            handler = self.get_rb_handler()
            found_entries = handler.query(query)
            for entry in found_entries:
                library['entries'].append(get_song(entry))
            library[SEARCH_TYPES[search_by]] = value
        return library
