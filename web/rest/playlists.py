import logging

from web.rest import RBRest
from serve.request import ClientError
from rhythmweb.model import get_playlist
from rhythmweb.controller import Source

from collections import defaultdict

log = logging.getLogger(__name__)

class Page(RBRest):
    
    def get(self):
        source = Source(self.get_rb_handler())
        
        if not self.has_path_parameters():
            playlists = source.get_sources()
            if not playlists:
                return None
            plst = defaultdict(lambda:[])
            for playlist in playlists:
                plst['playlists'].append(get_playlist(playlist))
            return plst
        else:
            playlist_id = self.to_int(self.get_path_parameter(0), "playlist")
            try:
                playlist = source.get_source(playlist_id) 
                return get_playlist(playlist)
            except IndexError:
                raise ClientError('there is no playlist with id {}'.format(playlist_id))
            
    
    def post(self):
        action = self.get_parameter('action', True)

        if self.has_parameter('playlist'):
            source_id = self.to_int(self.get_parameter('playlist', True), "playlist")
        elif self.has_parameter('source'):
            source_id = self.to_int(self.get_parameter('source', True), "source")
        else:
            raise ClientError('no "source" parameter')

        source = Source(self.get_rb_handler())

        try:
            if action == 'enqueue':
                count = source.enqueue_by_id(source_id)
                if count is None:
                    return {'result': 'BAD'}
                return {'count': count, 'result': 'OK'}
                    
            elif action == 'play_source':
                if source.play_source(source_id):
                    return {'result': 'OK'}
                else:
                    return {'result': 'BAD'}
            raise ClientError('Unknown action {}'.format(action))
        except IndexError:
            raise ClientError('there is no playlist with id {}'.format(source_id))
