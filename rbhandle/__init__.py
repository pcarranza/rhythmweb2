from .player import PlayerHandler
from .entry import EntryHandler
from .query import QueryHandler
from .queue import QueueHandler
from .source import SourceHandler

import logging
log = logging.getLogger(__name__)


class RBHandler(PlayerHandler, EntryHandler, QueryHandler, QueueHandler, SourceHandler):
    '''
    Rhythmbox shell wrapper, provides player, queue, playlist, 
    artist/album/genre count cache and max instances 
    and some other functionallities
    '''
    
    def __init__(self, shell):
        '''
        Creates a new rhythmbox handler, wrapping the RBShell object that gets 
        by parameter
        '''
        if shell is None:
            log.error('Setting shell object to None')
            raise Exception('Shell object cannot be null')

        log.debug('Setting shell object')
        PlayerHandler.__init__(self, shell)
        EntryHandler.__init__(self, shell)
        QueryHandler.__init__(self, shell)
        QueueHandler.__init__(self, shell)
        SourceHandler.__init__(self, shell)
        
        log.debug('rbhandler loaded')
