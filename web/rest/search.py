from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from serve.rest.json import JSon
from web.rest import Song
from rbhandle import InvalidQueryException
from serve.request import ServerException


class Page(BaseRest, Loggable):
    
    def get(self):
        self.debug('GET search')
        handler = self._components['RB']
        filter = self.get_filter()
        
        if filter:
            for f in filter:
                self.debug('Searching for %s: \"%s\"' % (f, str(filter[f])))
        else:
            self.debug('Filter is empty')
        
        try:
            entry_ids = handler.query(filter)
        except InvalidQueryException, e:
            raise ServerException(501, 'bad request, %s' % e.message)
        
        json = JSon()
        entries = []
        
        for id in entry_ids:
            entry = Song.get_song_as_JSon(handler, id)
            entries.append(entry)
        
        if entries:
            json.put('entries', entries)
        
        return json
        
        
        
    def post(self):
        self.debug('POST search')
        return self.get()
        
        
    def get_filter(self):
        self.debug('get_filter')
        filter = {}

        if not self._path_params is None:
            self.debug('Getting type from path_params')
            if 'song' in self._path_params:
                filter['type'] = 'song'
            elif 'iradio' in self._path_params:
                filter['type'] = 'iradio'
            elif 'podcast' in self._path_params:
                filter['type'] = 'podcast-post'
            else:
                self.debug('No valid type in path_params')
                
            if 'first' in self._path_params:
                pos = self._path_params.index('first')
                if len(self._path_params) > pos + 1:
                    filter['first'] = self._path_params[pos + 1]

            if 'limit' in self._path_params:
                pos = self._path_params.index('limit')
                if len(self._path_params) > pos + 1:
                    filter['limit'] = self._path_params[pos + 1]
        
        
        if not self._parameters is None:
            self.debug('Reading POST parameters')
            
            if not 'type' in filter and 'type' in self._parameters:
                filter['type'] = self.unpack_value(self._parameters['type'])
            
            if 'artist' in self._parameters:
                filter['artist'] = self.unpack_value(self._parameters['artist'])
                
            if 'title' in self._parameters:
                filter['title'] = self.unpack_value(self._parameters['title'])
                
            if 'album' in self._parameters:
                filter['album'] = self.unpack_value(self._parameters['album'])
                
            if 'rating' in self._parameters:
                rating = self.unpack_value(self._parameters['rating'])
                
                if rating.isdigit():
                    irating = int(rating)
                else:
                    irating = len(str(rating).strip())
                    
                filter['rating'] = irating
                
            if 'from' in self._parameters:
                filter['from'] = self.unpack_value(self._parameters['from'])
                
            if 'size' in self._parameters:
                filter['size'] = self.unpack_value(self._parameters['size'])
        
            if 'first' in self._parameters:
                filter['first'] = self.unpack_value(self._parameters['first'])
        
            if 'limit' in self._parameters:
                filter['limit'] = self.unpack_value(self._parameters['limit'])
                
            if 'all' in self._parameters:
                all = self.unpack_value(self._parameters['all'])
                filter['all'] = all
                return filter
            
        
        return filter
    
    
