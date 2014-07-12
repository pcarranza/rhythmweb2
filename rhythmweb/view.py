
from rhythmweb.app import route
from rhythmweb.controller import Player, Song, Queue, Query
from rhythmweb.utils import to_int

import logging
log = logging.getLogger(__name__)


MEDIA_TYPES = {'song' : 'song',
                'radio' : 'iradio',
                'iradio' : 'iradio',
                'podcast' : 'podcast-post',
                'podcast-post' : 'podcast-post'}


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


@route('/rest/search/<media_type?>/<first_constraint?>/<first_value?>/<second_constraint?>/<second_value?>')
def search(*args, **kwargs):
    try:
        query = parse_search_args(args)
        if kwargs:
            query.update(kwargs)
        validate_query(query)
        log.debug('Running query {}'.format(query))
        return Query().query(query)
    except:
        log.error('Error while running query', exc_info=True)
        raise ValueError('Invalid query')
        

def parse_search_args(args):
    if not args:
        return {}
    query = {}
    query_type = MEDIA_TYPES.get(args[0], None)
    if not query_type:
        log.debug('No media type for "%s"' % args[0])
        values = args
    else:
        log.debug('Searching for media type "%s"' % args[0])
        query['type'] = query_type
        values = args[1:]

    if values:
        for key, value in zip(values[::2], values[1::2]):
            if not (key or value): continue
            log.debug('Appending constraint {}={}'.format(key, value))
            query[key] = value
    return query


def validate_query(query):
    if not query:
        return
    if 'rating' in query:
        rating = query['rating']
        query['rating'] = rating if rating.isdigit() else len(rating)
    if 'type' in query:
        query['type'] = query['type'] if query['type'] in MEDIA_TYPES else None

