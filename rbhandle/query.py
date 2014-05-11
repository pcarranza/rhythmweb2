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

from gi.repository import RB, GLib
from .model import ModelHandler

import logging
log = logging.getLogger(__name__)

TYPE_SONG = 'song'
TYPE_RADIO = 'iradio'
TYPE_PODCAST = 'podcast-post'

class QueryHandler(object):
    
    def __init__(self, shell):
        self.shell = shell
        self.db = shell.props.db
        
        self.__media_types = {}
        for t in [TYPE_SONG, TYPE_RADIO, TYPE_PODCAST]:
            rb_type = self.db.entry_type_get_by_name(t)
            self.__media_types[t] = rb_type

    
    def search_song(self, filter):
        '''
        Performs a query for entry type "song" with the provided filters 
        '''
        log.info('Searching for a song with filter %s' % filter)
        return self.search(filter, TYPE_SONG)
    
    
    def search_radio(self, filter):
        '''
        Performs a query for entry type "radio" with the provided filters 
        '''
        log.info('Searching for a radio with filter %s' % filter)
        return self.search(filter, TYPE_RADIO)
    
    
    def search_podcast(self, filter):
        '''
        Performs a query for entry type "podcast" with the provided filters 
        '''
        log.info('Searching for a podcast with filter %s' % filter)
        return self.search(filter, TYPE_PODCAST)
    
    
    def search(self, filter, type):
        '''
        Performs a query for provided entry type with the provided filters 
        '''
        filters = {}
        filters['type'] = type
        filters['all'] = filter
        
        return self.query(filters)
    
    
    def query_all(self, mtype, min_play_count, min_rating, parameters, query_for_all=False):
        '''
        Performs the quey
        '''
        db = self.db
        log.info('Querying...')
        query_model = RB.RhythmDBQueryModel.new_empty(db)
        query_model.set_sort_order(RB.RhythmDBQueryModel.album_sort_func, None, False)

        if mtype is None:
            query_for_type = None
        else:
            query_for_type = (RB.RhythmDBQueryType.EQUALS, \
                RB.RhythmDBPropType.TYPE, \
                self.db.entry_type_get_by_name(mtype))
        
        
        if query_for_all: # equivalent to use an OR (many queries)
            log.info('Query for all parameters separatedly')
            for parameter in parameters:
                query = GLib.PtrArray()
                if not query_for_type is None:
                    log.info('Appending Query for type \"%s\"...' % mtype)
                    db.query_append_params(query, query_for_type[0], query_for_type[1], query_for_type[2])
                log.info('Appending Query for parameter "%s"~"%s"...' % (parameter[1], parameter[2]))
                db.query_append_params(query, parameter[0], parameter[1], parameter[2]) # Append parameter

                self.append_rating_query(query, min_rating) # Append
                self.append_play_count_query(query, min_play_count)
                log.info("Running query")
                db.do_full_query_parsed(query_model, query) # Do query

        else:
            log.info('Query for all parameters in one only full search')
            query = GLib.PtrArray()
            if not query_for_type is None:
                log.info('Appending Query for type \"%s\"...' % mtype)
                db.query_append_params(query, query_for_type[0], query_for_type[1], query_for_type[2])
            self.append_rating_query(query, min_rating)
            self.append_play_count_query(query, min_play_count)
            for parameter in parameters:
                log.info('Appending Query for parameter "%s"~"%s"...' % (parameter[1], parameter[2]))
                db.query_append_params(query, parameter[0], parameter[1], parameter[2])        
            log.info("Running query")
            db.do_full_query_parsed(query_model, query)

        return query_model
    
    
    def append_play_count_query(self, query, play_count):
        '''
        Appends a min playcount filter to the given query
        '''
        if play_count > 0:
            log.info('Appending min play count %d' % play_count)
            self.db.query_append_params(query, RB.RhythmDBQueryType.GREATER_THAN, RB.RhythmDBPropType.PLAY_COUNT, play_count)
    
    
    def append_rating_query(self, query, rating):
        '''
        Appends a min rating filter to the given query
        '''
        if rating > 0:
            log.info('Appending min rating query %d' % rating)
            self.db.query_append_params(query, \
                    RB.RhythmDBQueryType.GREATER_THAN, \
                    RB.RhythmDBPropType.RATING, \
                    rating)
    
    
    def query(self, filters):
        '''
        Performs a query with the provided filters 
        '''
        log.debug('RBHandler.query...')
        if filters is None or not filters:
            log.info('No filters, returning empty result')
            return []
        
        mtype = None
        rating = 0
        play_count = 0
        first = 0
        limit = 100
        all = None
        searches = None
        prop_match = RB.RhythmDBQueryType.FUZZY_MATCH
        
        if filters:
            for key in filters:
                value = filters[key]
                if type(value) is str:
                    log.debug('Searching for %s: "%s"' % (key, value))
                else:
                    log.warning('Searching for %s but type is "%s"' % (key, type(value)))
            
            if 'exact-match' in filters:
                prop_match = RB.RhythmDBQueryType.EQUALS
                
            if 'first' in filters:
                first = str(filters['first'])
                if not first.isdigit():
                    raise InvalidQueryException('Parameter first must be a number, it actually is \"%s\"' % first)
                first = int(first)
                
            if 'limit' in filters:
                limit = str(filters['limit'])
                if not limit.isdigit():
                    raise InvalidQueryException('Parameter limit must be a number, it actually is \"%s\"' % limit)
                limit = int(limit)
            
            if 'type' in filters:
                mtype = filters['type']
                log.debug('Appending query for type \"%s\"' % mtype)
                if mtype not in self.__media_types:
                    log.error('Media \"%s\" not found' % mtype)
                    raise InvalidQueryException('Unknown media type \"%s\"' % mtype)
                else:
                    log.debug('Type %s added to query' % mtype)
            
            if 'rating' in filters:
                rating = str(filters['rating'])
                log.debug('Appending query for rating \"%s\"' % rating)
                if not rating.isdigit():
                    raise InvalidQueryException('Parameter rating must be a float, it actually is \"%s\"' % rating)
                rating = float(rating)
                
            if 'play_count' in filters:
                play_count = str(filters['play_count'])
                log.debug('Appending query for play_count \"%s\"' % play_count)
                if not play_count.isdigit():
                    raise InvalidQueryException('Parameter play_count must be an int, it actually is \"%s\"' % play_count)
                play_count = int(play_count)
                
            if 'all' in filters:
                all = []
                all_filter = filters['all'].lower()
                log.debug('Append all kind of filters with value "%s"' % all_filter)
                all.append((prop_match, \
                    RB.RhythmDBPropType.ARTIST_FOLDED, \
                    all_filter))
                all.append((prop_match, \
                    RB.RhythmDBPropType.TITLE_FOLDED, \
                    all_filter))
                all.append((prop_match, \
                    RB.RhythmDBPropType.ALBUM_FOLDED, \
                    all_filter))
                all.append((prop_match, \
                    RB.RhythmDBPropType.GENRE_FOLDED, \
                    all_filter))
                
            else:
                searches = []
                if 'artist' in filters:
                    log.debug('Appending query for artist \"%s\"' % filters['artist'])
                    searches.append((prop_match, \
                        RB.RhythmDBPropType.ARTIST_FOLDED, \
                        filters['artist'].lower()))
                    
                if 'title' in filters:
                    log.debug('Appending query for title \"%s\"' % filters['title'])
                    searches.append((prop_match, \
                        RB.RhythmDBPropType.TITLE_FOLDED, \
                        filters['title'].lower()))
                    
                if 'album' in filters:
                    log.debug('Appending query for album \"%s\"' % filters['album'])
                    searches.append((prop_match, \
                        RB.RhythmDBPropType.ALBUM_FOLDED, \
                        filters['album'].lower()))
                    
                if 'genre' in filters:
                    log.debug('Appending query for genre \"%s\"' % filters['genre'])
                    searches.append((prop_match, \
                        RB.RhythmDBPropType.GENRE_FOLDED, \
                        filters['genre'].lower()))
                
                    
        if not all is None:
            log.info('Querying for all...')
            query_model = self.query_all(mtype, play_count, rating, all, True)
              
        elif searches:
            log.info('Querying for each...')
            query_model = self.query_all(mtype, play_count, rating, searches)
        
        elif mtype is None:
            log.info('No search filter defined, querying for default')
            query_model = self.query_all(TYPE_SONG, play_count, rating, searches)
            
        else:
            log.info('Search for type only, querying for type')
            query_model = self.query_all(mtype, play_count, rating, searches)
        
        
        log.debug('RBHandler.query executed, loading results...')
        entries = []
        m = ModelHandler(self.shell)
        m.loop_query_model(func=entries.append, query_model=query_model, first=first, limit=limit)
        log.debug('RBHandler.query executed, returning results...')
        return entries


class InvalidQueryException(Exception):
    
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

