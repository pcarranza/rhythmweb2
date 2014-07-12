
from rhythmweb.app import route
from rhythmweb.controller import Player, Song, Queue, Query
from rhythmweb.utils import to_int, to_float

import logging
log = logging.getLogger(__name__)


MEDIA_TYPES = {'song' : 'song',
                'radio' : 'iradio',
                'iradio' : 'iradio',
                'podcast' : 'podcast-post',
                'podcast-post' : 'podcast-post'}

SEARCH_TYPES = {'artists' : 'artist', 
                'genres' : 'genre', 
                'albums' : 'album'}

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


@route('/rest/player')
def play(**kwargs):
    if not kwargs:
        raise TypeError
    action = kwargs.get('action', None)
    if not action:
        raise ValueError('No action')
    log.debug('Calling action "{}"'.format(action))
    player = Player()
    if action in ('play_pause', 'next', 'previous', 'seek', 'play_entry',
                    'mute', 'set_volume'):
        method = getattr(player, action)
        method(**parse_player_args(kwargs))
    elif action in ('enqueue', 'dequeue', 'shuffle_queue', 'clear_queue'):
        queue = Queue()
        method = getattr(queue, action)
        method(**parse_player_args(kwargs))
    else:
        raise ValueError('action "{}" is not supported'.format(action))
    status = player.status()
    status['last_action'] = action
    return status
    

def parse_player_args(player_arguments):
    log.debug('parsing player arguments {}'.format(player_arguments))
    kwargs = {}
    if 'time' in player_arguments:
        kwargs['time'] = to_int(player_arguments['time'],
                'time must be a number')
    if 'entry_id' in player_arguments:
        entry_id = player_arguments['entry_id']
        if ',' in entry_id:
            entries = [int(entry) for entry in entry_id.split(',')]
        else:
            entries = int(entry_id)
        kwargs['entry_id'] = entries
    if 'volume' in player_arguments:
        kwargs['volume'] = to_float(player_arguments['volume'],
            'volume must be number')
    return kwargs


@route('/rest/library/<constraint?>/<value?>')
def library(*args):
    search_by, value = args
    if not search_by or not value:
        raise ValueError('no parameters')
    if search_by not in SEARCH_TYPES:
        raise ValueError('Invalid library filter "{}"'.format(search_by))
    value = str(value).replace('+', ' ')
    search_type = SEARCH_TYPES[search_by]
    query = {
            'type': 'song',
            search_type: value,
            'exact-match': True,
            'limit': 0
            }
    library = Query().query(query)
    library[search_type] = value
    return library
    
