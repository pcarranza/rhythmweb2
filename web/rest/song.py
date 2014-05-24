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
        return self.get_int_path_parameter(0, 'song id is not a number')

    def __not_found(self):
        return 'Song {} not found'.format(self.get_song_id())
