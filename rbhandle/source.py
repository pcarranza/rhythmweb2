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


from .model import ModelHandler

import logging
log = logging.getLogger(__name__)

RB_SOURCELIST_MODEL_COLUMN_PLAYING = 0
RB_SOURCELIST_MODEL_COLUMN_PIXBUF = 1
RB_SOURCELIST_MODEL_COLUMN_NAME = 2
RB_SOURCELIST_MODEL_COLUMN_SOURCE = 3
RB_SOURCELIST_MODEL_COLUMN_ATTRIBUTES = 4
RB_SOURCELIST_MODEL_COLUMN_VISIBILITY = 5
RB_SOURCELIST_MODEL_COLUMN_IS_GROUP = 6
RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY = 7

SOURCETYPE_PLAYLIST = 'playlist'
SOURCETYPE_SOURCE = 'source'

class SourceHandler(object):
    
    def __init__(self, shell):
        self.shell = shell
    
    def play_source(self, source):
        log.info('Set source playing')
        if self.get_playing_status():
            self.play_pause()
        self.shell.props.shell_player.set_playing_source(source.source)
        return self.play_pause()
    
    def __get_sources(self, all_sources=False):
        '''
        Returns a list with all sources registered
        '''
#        index = 0
        sources = []
#        for sourcelist in self.shell.props.sourcelist_model:
#            category = sourcelist[RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY]
#            if category == rb.SOURCE_GROUP_CATEGORY_PERSISTENT or \
#                    category == rb.SOURCE_GROUP_CATEGORY_REMOVABLE:
#                for playlist in sourcelist.iterchildren():
#                    sources.append(RBSource(index, playlist, SOURCETYPE_PLAYLIST))
#                    index += 1
#            elif category == rb.SOURCE_GROUP_CATEGORY_FIXED:
#                for source in sourcelist.iterchildren():
#                    if all_sources:
#                        sources.append(RBSource(index, source, SOURCETYPE_SOURCE))
#                    index += 1
        return self.get_sources()
    
    def get_source(self, source_index):
        log.info('Getting source with index %d' % source_index)
        
        if not type(source_index) is int:
            raise Exception('source_index parameter must be an int')
        
        index = 0
        sources = self.__get_sources(True)
        for source in sources:
            if source.index == source_index:
                log.debug('Returning source with index %d' % index)
                return source
            index += 1
        
        return None
        
    def get_source_entries(self, source, limit=100):
        log.info('Getting source entries')
        entries = []
        m = ModelHandler(self.shell)
        if not source is None:
            m.loop_query_model(func=entries.append, \
                                   query_model=source.query_model, \
                                   limit=limit)
        return entries
    
    def get_playlists(self):
        '''
        Returns all registered playlists 
        '''
        return self.__get_wrapped_sources(self.shell.props.playlist_manager.get_playlists())
    
    def get_sources(self):
        '''
        Returns all fixed sources 
        '''
        return self.__get_sources(True)
    
    def __get_wrapped_sources(self, sourcelist):
        sources = []
        index = 0
        for source in sourcelist:
            source = RBSource(index, source)
            sources.append(source)
            index+= 1
        
        return sources
    
    def enqueue_source(self, source):
        '''
        Enqueues in the play queue the given playlist 
        '''
        log.info('Enqueuing source')
        
        if not source:
            return 0
        
        # playlist.add_to_queue(self.shell.props.queue_source)
        # This way we will know how many songs are added
        m = ModelHandler(self.shell)
        return m.loop_query_model(
                   func=self.enqueue, 
                   query_model=source.query_model)


class RBSource(object):
    '''
    Source wrapper, loads all data on initialization
    '''
    def __init__(self, index, entry, source_type='playlist'):
        self.id = index
        self.index = index
        self.source_type = source_type
        self.is_playing = False # entry[RB_SOURCELIST_MODEL_COLUMN_PLAYING] (Check agains shell.get_playing_source)
        self.pixbuf = entry.props.pixbuf # entry[RB_SOURCELIST_MODEL_COLUMN_PIXBUF]
        self.name = entry.props.name # entry[RB_SOURCELIST_MODEL_COLUMN_NAME]
        self.source = entry
        self.query_model = entry.props.query_model
        self.attributes = None # entry[RB_SOURCELIST_MODEL_COLUMN_ATTRIBUTES]
        self.visibility = None # entry[RB_SOURCELIST_MODEL_COLUMN_VISIBILITY]
        self.is_group = False # entry[RB_SOURCELIST_MODEL_COLUMN_IS_GROUP]
        self.group_category = None #entry[RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY]

