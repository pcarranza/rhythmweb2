
from rhythmweb.app import route
from rhythmweb.controller import Player, Song, Queue, Query, Source, query_library
from rhythmweb.utils import to_int, to_float

import logging
log = logging.getLogger(__name__)


MEDIA_TYPES = {'song' : 'song',
                'radio' : 'iradio',
                'iradio' : 'iradio',
                'podcast' : 'podcast-post',
                'podcast-post' : 'podcast-post'}

SEARCH_TYPES = {'artists', 'genres', 'albums'}

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
            log.info('Setting rating for song %d=%d', song_id, rating)
            handler.set_rating(song, rating)
    log.debug('Returning song %s', song)
    return song


@route('/rest/queue')
def queue():
    handler = Queue()
    log.debug('Returning queue')
    return handler.get_queue()


@route('/rest/search/<media_type?>/<first_constraint?>/<first_value?>/<second_constraint?>/<second_value?>')
def search(*args, **kwargs):
    try:
        query = parse_search_args(args)
        if kwargs:
            query.update(kwargs)
        validate_query(query)
        log.info('Running query {}'.format(query))
        return Query().query(query)
    except:
        log.error('Error while running query', exc_info=True)
        raise ValueError('Invalid query')
        

def parse_search_args(args):
    query = {}
    query_type = MEDIA_TYPES.get(args[0], None)
    if not query_type:
        log.warn('No media type for "%s"' % args[0])
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
        log.info('Running player action {} with args {}'.format(action, kwargs))
        method(**parse_player_args(kwargs))
    elif action in ('enqueue', 'dequeue', 'shuffle_queue', 'clear_queue'):
        queue = Queue()
        method = getattr(queue, action)
        log.info('Running queue action {} with args {}'.format(action, kwargs))
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


@route('/rest/library/<search_for>')
def library(search_for):
    if search_for not in SEARCH_TYPES:
        raise ValueError('Invalid library filter "{}"'.format(search_for))
    return query_library(search_for)

    
@route('/rest/playlists/<id?:int>')
def playlists(playlist_id, **kwargs):
    source = Source()
    if kwargs: # POST
        action = kwargs.get('action', None)
        if not action:
            raise ValueError('no "action" parameter')
        if action not in ['enqueue', 'play_source']:
            raise ValueError('Unknown action {}'.format(action))
        playlist_id = kwargs['playlist'] if 'playlist' in kwargs else kwargs.get('source', None)
        if playlist_id is None:
            raise ValueError('no "source" parameter')
        playlist_id = to_int(playlist_id, 'playlist id must be a number')
        try:
            if action == 'enqueue':
                count = source.enqueue_by_id(playlist_id)
                log.info('Enqueued source {}, {} entries'.format(playlist_id, count))
                return {'result': 'BAD'} if count is None else {'count': count, 'result': 'OK'}
            # elif action == 'play_source':
            log.info('Playing source {}'.format(playlist_id))
            return {'result': 'OK'} if source.play_source(playlist_id) else {'result': 'BAD'}
        except IndexError:
            raise ValueError('there is no playlist with id {}'.format(playlist_id))
    elif playlist_id is None: # GET
        return {'playlists': source.get_playlists()}
    else:
        try:
            return source.get_playlist(playlist_id)
        except IndexError:
            raise ValueError('there is no playlist with id {}'.format(playlist_id))
