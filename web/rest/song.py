from web.rest import RBRest
from rhythmweb.controller import Song

import logging
log = logging.getLogger(__name__)

class Page(RBRest):

    def get(self):
        song_id = self.get_song_id()
        return Song().find_by_id(song_id)

    def post(self):
        handler = Song()
        song_id = self.get_song_id()
        rating = self.get_rating()
        song = handler.find_by_id(song_id)
        if not song:
            log.warning('Could not find song with id {} to rate'.format(song_id)) 
            return None
        song['rating'] = rating
        handler.rate(song)
        return song

    def get_song_id(self):
        return self.to_int(self.get_path_parameter(0), 
                'song id is not a number')

    def get_rating(self):
        return self.to_int(self.get_parameter('rating', True),
                'rating must be a number')
