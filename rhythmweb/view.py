
from rhythmweb.app import route
from rhythmweb.controller import Player

import logging
log = logging.getLogger(__name__)


@route('/rest/status')
def get_status():
    log.debug('Returning status')
    return Player().status()

@route('/rest/song/<song>')
def get_song(song_id, **kwargs):
    return None
    
