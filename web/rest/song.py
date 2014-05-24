from serve.request import ServerException
from web.rest import RBRest
from rhythmweb.model import get_song

import logging
log = logging.getLogger(__name__)

class Page(RBRest):

    def get(self):
        song_id = self.get_song_id()
        if not song_id:
            return None
        rb = self.get_rb_handler()
        entry = rb.load_entry(rb.get_entry(song_id))
        return get_song(entry)

    def post(self):
        song_id = self.get_song_id()
        if not song_id:
            return None
        rating = self.get_int_parameter('rating')
        if not rating is None:
            log.info('Setting Rating %s for song "%s"' % (rating, song_id))
            self.get_rb_handler().set_rating(song_id, rating)
        return self.get()

    def get_song_id(self):
        log.debug('Getting song id from path parameters')
        if not self.has_path_parameters():
            return None
        if len(self.get_path_parameters()) > 1:
            raise ServerException(400, 'Bad Request: no song id in path')
        log.debug('Reading path parameters index 0')
        song_id = self.get_path_parameter(0)
        try:
            song_id = int(song_id)
        except:
            raise ServerException(400, 'Bad Request: song id is not a number')
        return song_id

    def __not_found(self):
        return 'Song {} not found'.format(self.get_song_id())
