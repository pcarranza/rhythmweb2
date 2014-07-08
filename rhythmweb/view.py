
from rhythmweb.app import route
from rhythmweb.controller import Player, Song, Queue
from rhythmweb.utils import to_int

import logging
log = logging.getLogger(__name__)


@route('/rest/status')
def status():
    log.debug('Returning status')
    return Player().status()


@route('/rest/song/<song:int>')
def song(song_id, **kwargs):
    handler = Song()
    song = handler.find_by_id(song_id)
    if song:
        rating = to_int(kwargs.get('rating', None), 'rating must be a number')
        if not rating is None:
            handler.set_rating(song, rating)
    return song


@route('/rest/queue')
def queue():
    handler = Queue()
    return handler.get_queue()
