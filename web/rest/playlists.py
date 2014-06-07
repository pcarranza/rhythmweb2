import logging

from web.rest import RBRest
from serve.request import ClientError
from rhythmweb.model import get_playlist
from collections import defaultdict

log = logging.getLogger(__name__)

class Page(RBRest):
    
    def get(self):
        handler = self.get_rb_handler()
        
        if not self.has_path_parameters():
            playlists = handler.get_playlists()
            if not playlists:
                return None
            plst = defaultdict(lambda:[])
            for playlist in playlists:
                plst['playlists'].append(get_playlist(playlist))
            return plst
        
        else:
            playlist_id = self.get_path_parameter(0)
            if not playlist_id.isdigit():
                raise ClientError('path parameter must be an int')
            playlist_id = int(playlist_id)
            log.debug('Loading playlist with id %d' % playlist_id)
            playlist = self.get_playlist_by_id(playlist_id) 
            return get_playlist(playlist)
            
    
    def post(self):
        action = self.get_parameter('action', True)

        if self.has_parameter('playlist'):
            source_id = self.get_parameter('playlist', True)
        elif self.has_parameter('source'):
            source_id = self.get_parameter('source', True)
        else:
            raise ClientError('no "source" parameter')

        source_id = int(source_id)
        handler = self.get_rb_handler()
        
        if not action:
            raise ClientError('no "action" parameter')

        playlist = self.get_playlist_by_id(source_id) 
        if not playlist:
            raise ClientError('there is no playlist with id %d', source_id)

        result = {}
        if action == 'enqueue':
            count = handler.enqueue_source(playlist)
            result['count'] = count
            if count > 0:
                result['result'] = 'OK'
                
        elif action == 'play_source':
            if handler.play_source(playlist):
                result['result'] = 'OK'
            else:
                result['result'] = 'BAD'
            
        return result

    def get_playlist_by_id(self, playlist_id):
        handler = self.get_rb_handler()
        playlists = handler.get_playlists()
        if not playlists:
            return None
        try:
            return playlists[playlist_id]
        except IndexError:
            raise ClientError('There is no playlist with id %d' % playlist_id)
