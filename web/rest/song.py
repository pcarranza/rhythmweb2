from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from serve.request import ServerException
from web.rest import Song

class Page(BaseRest, Loggable):
    
    def get(self):
        if not self._path_params:
            return None
        
        params = self._path_params
        
        if len(params) != 1:
            raise ServerException(400, 'Bad Request')
        
        song_id = int(params[0])
        
        handler = self._components['RB']
        
        return Song.get_song_as_JSon(handler, song_id)
        
        
    def post(self):
        pass
        
        
    def not_found(self):
        return 'Song not found :('
    
    
    

