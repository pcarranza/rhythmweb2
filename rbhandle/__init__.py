# -*- coding: utf-8 -
# Rhythmweb - Rhythmbox web REST + Ajax environment for remote control
# Copyright (C) 2010  Pablo Carranza
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
