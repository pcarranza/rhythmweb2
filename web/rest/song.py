from web.rest import RBRest
from rhythmweb.controller import Song

import logging
log = logging.getLogger(__name__)

class Page(RBRest):

    def get(self):
        song_id = self.get_song_id()
        return self.controller.find_by_id(song_id)

    def post(self):
        song_id = self.get_song_id()
        rating = self.get_rating()
        song = self.controller.find_by_id(song_id)
        if not song:
            log.warning('Could not find song with id {} to rate'.format(song_id)) 
            return None
        song['rating'] = rating
        self.controller.rate(song)
        return song

    def get_song_id(self):
        return self.get_int_path_parameter(0, 'song id is not a number')

    def get_rating(self):
        return self.get_int_parameter('rating')

    @property
    def controller(self):
        return Song(self.get_rb_handler())

    def __not_found(self):
        return 'Song {} not found'.format(self.get_song_id())
