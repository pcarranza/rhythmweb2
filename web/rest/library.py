from web.rest import RBRest
from serve.app import ClientError
from rhythmweb.controller import Query
from collections import defaultdict

SEARCH_TYPES = {'artists' : 'artist', 'genres' : 'genre', 'albums' : 'album'}

class Page(RBRest):
    
    def get(self):
        if not self.has_path_parameters():
            raise ClientError('no parameters')

        search_by = self.get_path_parameter(0)
        if search_by not in SEARCH_TYPES:
            raise ClientError('path parameter "%s" not supported' % search_by)
        
        if self.get_path_parameters_size() == 1:
            raise ClientError('path params by type only search is not supported now')
        else:
            value = self.get_path_parameter(1)
            value = str(value).replace('+', ' ')
            
            query = {}
            query['type'] = 'song'
            query[SEARCH_TYPES[search_by]] = value
            query['exact-match'] = True
            query['limit'] = 0
            library = Query().query(query)
            library[SEARCH_TYPES[search_by]] = value
        return library
