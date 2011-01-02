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

import gconf
import urllib
import rb, rhythmdb

from serve.log.loggable import Loggable

TYPE_SONG = 'song'
TYPE_RADIO = 'iradio'
TYPE_PODCAST = 'podcast-post'

PLAY_LOOP = '-loop'

ORDER_LINEAR = 'linear'
ORDER_SHUFFLE = 'shuffle'
ORDER_SHUFFLE_BY_AGE_AND_RATING = 'random-by-age-and-rating'
ORDER_SHUFFLE_BY_AGE = 'random-by-age'
ORDER_SHUFFLE_BY_RATING = 'random-by-rating'
ORDER_SHUFFLE_EQUALS = 'random-equal-weights'

PLAY_ORDER_KEY = '/apps/rhythmbox/state/play_order'


class RBHandler(Loggable):
    
    _instance = None
    
    _media_types = None
    _play_orders = None
    _play_toggle_loop = None
    _play_toggle_shuffle = None
    
    def __print_state(self, status):
        self.debug('STATUS FROM %s' % status)
#        self.debug('SHELL object %s' % self._shell)
#        self.debug('DB object %s' % self._db)
#        self.debug('PLAYER object %s' % self._player)
#        self.debug('GCONF object %s' % self._gconf)
        
        
    def __init__(self, shell):
        self.debug('Creating new RBHandler object')
        
        if shell is None:
            self.error('Setting shell object to None')
            raise Exception('Shell object cannot be null')
        else:
            self.debug('Setting shell object')
        
        self._shell = shell
        self._db = shell.props.db
        self._player = shell.get_player()
        self._gconf = gconf.client_get_default()
        self._media_types = {}
        for type in [TYPE_SONG, TYPE_RADIO, TYPE_PODCAST]:
            rb_type = self._db.entry_type_get_by_name(type)
            self._media_types[type] = rb_type
        
        self.__print_state('__init__')

        
        LINEAR_LOOP = "%s%s" % (ORDER_LINEAR, PLAY_LOOP)
        SHUFFLE_LOOP = "%s%s" % (ORDER_SHUFFLE, PLAY_LOOP)
        
        self._play_orders = {
            ORDER_LINEAR : ORDER_LINEAR,
            ORDER_SHUFFLE : ORDER_SHUFFLE,
            LINEAR_LOOP : LINEAR_LOOP,
            SHUFFLE_LOOP : SHUFFLE_LOOP,
            ORDER_SHUFFLE_EQUALS : ORDER_SHUFFLE_EQUALS,
            ORDER_SHUFFLE_BY_AGE : ORDER_SHUFFLE_BY_AGE,
            ORDER_SHUFFLE_BY_RATING : ORDER_SHUFFLE_BY_RATING,
            ORDER_SHUFFLE_BY_AGE_AND_RATING: ORDER_SHUFFLE_BY_AGE_AND_RATING}
        
        self._play_toggle_loop = {
            ORDER_LINEAR : LINEAR_LOOP,
            LINEAR_LOOP : ORDER_LINEAR,
            ORDER_SHUFFLE : SHUFFLE_LOOP,
            SHUFFLE_LOOP : ORDER_SHUFFLE}
        
        self._play_toggle_shuffle = {
            ORDER_LINEAR : ORDER_SHUFFLE,
            ORDER_SHUFFLE : ORDER_LINEAR,
            LINEAR_LOOP : SHUFFLE_LOOP,
            SHUFFLE_LOOP : LINEAR_LOOP,
            ORDER_SHUFFLE_EQUALS : ORDER_LINEAR,
            ORDER_SHUFFLE_BY_AGE : ORDER_LINEAR,
            ORDER_SHUFFLE_BY_RATING : ORDER_LINEAR,
            ORDER_SHUFFLE_BY_AGE_AND_RATING : ORDER_LINEAR}
    
    
    def get_playing_status(self):
        self.__print_state('get_playing_status')
        return self._player.get_playing() 
    
    
    def get_mute(self):
        self.__print_state('get_mute')
        return self._player.get_mute()
    
    
    def toggle_mute(self):
        self.__print_state('toggle_mute')
        if self.get_mute():
            self._player.set_mute(False)
        else:
            self._player.set_mute(True)
        
        
    def get_volume(self):
        self.__print_state('get_volume')
        return self._player.get_volume()
    
        
    def set_volume(self, volume):
        self.__print_state('set_volume')
        
        if not type(volume) is float:
            raise Exception('Volume must be a float')
        
        if volume > 1:
            self.warning('Volume cannot be set over 1')
            
        self._player.set_volume(volume)
        
        
    def get_playing_entry_id(self):
        self.__print_state('get_playing_entry_id')
        entry = self._player.get_playing_entry()
        if entry is None:
            return None
        
        return self._db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
    
        
    def play_entry(self, entry_id): # entry id
        self.__print_state('play_entry')
        self.info('Playing entry %s' % entry_id)
        
        entry = self._get_entry(entry_id)
        if not entry is None:
            if self.get_playing_status():
                self.play_pause()
            
            self._player.play_entry(entry)
    
        
    def set_rating(self, entry_id, rating):
        self.__print_state('set_rating')
        self.info('Setting rating %d to entry %s' % (rating, entry_id))
        entry = self._get_entry(entry_id)
        if not entry is None:
            self._db.set(entry, rhythmdb.PROP_RATING, rating)
    
        
    def search_song(self, filter):
        self.__print_state('search_song')
        self.info('Searching for a song with filter %s' % filter)
        return self.search(filter, TYPE_SONG)
    
    
    def search_radio(self, filter):
        self.__print_state('search_radio')
        self.info('Searching for a radio with filter %s' % filter)
        return self.search(filter, TYPE_RADIO)
    
    
    def search_podcast(self, filter):
        self.__print_state('search_podcast')
        self.info('Searching for a podcast with filter %s' % filter)
        return self.search(filter, TYPE_PODCAST)
    
    
    def search(self, filter, type):
        self.__print_state('search')
        filters = {}
        filters['type'] = type
        filters['all'] = filter
        
        return self.query(filters)
    
    
    def query(self, filters):
        self.__print_state('query')
        
        if filters is None:
            self.info('No filters, returning empty result')
            return []
        
        mtype = None
        rating = 0
        play_count = 0
        first = 0
        limit = 100
        all = None
        searches = None
        prop_match = rhythmdb.QUERY_PROP_LIKE
        
        if filters:
            
            if 'exact-match' in filters:
                prop_match = rhythmdb.QUERY_PROP_EQUALS
                
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
                #self.debug('Appending query for type \"%s\"' % mtype)
                if not self._media_types.has_key(mtype):
                    raise InvalidQueryException('Unknown media type \"%s\"' % filter['type'])
            
            if 'rating' in filters:
                rating = str(filters['rating'])
                self.debug('Appending query for rating \"%s\"' % rating)
                if not rating.isdigit():
                    raise InvalidQueryException('Parameter rating must be a float, it actually is \"%s\"' % rating)
                rating = float(rating)
                
            if 'play_count' in filters:
                play_count = str(filters['play_count'])
                self.debug('Appending query for play_count \"%s\"' % play_count)
                if not play_count.isdigit():
                    raise InvalidQueryException('Parameter play_count must be an int, it actually is \"%s\"' % play_count)
                play_count = int(play_count)
                
            if 'all' in filters:
                all = []
                all_filter = filters['all'].lower()
                all.append((prop_match, \
                    rhythmdb.PROP_ARTIST_FOLDED, \
                    all_filter))
                all.append((prop_match, \
                    rhythmdb.PROP_TITLE_FOLDED, \
                    all_filter))
                all.append((prop_match, \
                    rhythmdb.PROP_ALBUM_FOLDED, \
                    all_filter))
                all.append((prop_match, \
                    rhythmdb.PROP_GENRE_FOLDED, \
                    all_filter))
                
            else:
                searches = []
                if 'artist' in filters:
                    self.debug('Appending query for artist \"%s\"' % filters['artist'])
                    searches.append((prop_match, \
                        rhythmdb.PROP_ARTIST_FOLDED, \
                        filters['artist'].lower()))
                    
                if 'title' in filters:
                    self.debug('Appending query for title \"%s\"' % filters['title'])
                    searches.append((prop_match, \
                        rhythmdb.PROP_TITLE_FOLDED, \
                        filters['title'].lower()))
                    
                if 'album' in filters:
                    self.debug('Appending query for album \"%s\"' % filters['album'])
                    searches.append((prop_match, \
                        rhythmdb.PROP_ALBUM_FOLDED, \
                        filters['album'].lower()))
                    
                if 'genre' in filters:
                    self.debug('Appending query for genre \"%s\"' % filters['genre'])
                    searches.append((prop_match, \
                        rhythmdb.PROP_GENRE_FOLDED, \
                        filters['genre'].lower()))
                
                    
        if not all is None:
            self.info('Querying for all...')
            query_model = self._query_all(mtype, play_count, rating, all, True)
              
        elif searches:
            self.info('Querying for each...')
            query_model = self._query_all(mtype, play_count, rating, searches)
        
        elif mtype is None:
            self.info('No search filter defined, querying for default')
            query_model = self._query_all(TYPE_SONG, play_count, rating, searches)
            
        else:
            self.info('Search for type only, querying for type')
            query_model = self._query_all(mtype, play_count, rating, searches)

        
        entries = []
        self._loop_query_model(func=entries.append, query_model=query_model, first=first, limit=limit)
        return entries
    
    
    def _query_all(self, mtype, min_play_count, min_rating, parameters, query_for_all=False):
        self.info('Querying...')
        db = self._db
        if mtype == TYPE_SONG:
            query_model = db.query_model_new(\
                     db.query_new(), \
                     rhythmdb.rhythmdb_query_model_track_sort_func, \
                     0, \
                     db.query_model_new_empty())
        else:
            query_model = db.query_model_new_empty()
            
        
        #if not mtype is None:
        type = (rhythmdb.QUERY_PROP_EQUALS, \
            rhythmdb.PROP_TYPE, \
            self._db.entry_type_get_by_name(mtype))
        #else:
        #    type = None
        
        
        if query_for_all: # equivalent to use an OR (many queries)
            self.info('Query for all parameters separatedly')
            for parameter in parameters:
                self.info('Appending Query for parameter...')
                query = db.query_new()
                if not type is None:
                    self.info('Appending Query for type \"%s\"...' % mtype)
                    db.query_append(query, type)
                self._append_rating(query, min_rating)
                self._append_play_count(query, min_play_count)
                db.query_append(query, parameter)
                db.do_full_query_parsed(query_model, query)
        else:
            self.info('Query for all parameters in one only full search')
            query = db.query_new()
            if not type is None:
                self.info('Appending Query for type \"%s\"...' % mtype)
                db.query_append(query, type)
            self._append_rating(query, min_rating)
            self._append_play_count(query, min_play_count)
            for parameter in parameters:
                self.info('Appending Query for parameter...')
                db.query_append(query, parameter)
            db.do_full_query_parsed(query_model, query)
            
        return query_model
    
    
    def _append_play_count(self, query, play_count):
        if play_count > 0:
            self.info('Appending min play count %d' % play_count)
            db = self._db
            play_count_query = (rhythmdb.QUERY_PROP_GREATER, \
                rhythmdb.PROP_PLAY_COUNT, \
                play_count)
            db.query_append(query, play_count_query)


    def _append_rating(self, query, rating):
        if rating > 0:
            self.info('Appending min rating %d' % rating)
            db = self._db
            rating_query = (rhythmdb.QUERY_PROP_GREATER, \
                rhythmdb.PROP_RATING, \
                rating)
            db.query_append(query, rating_query)
    
    
    def get_play_order(self):
        self.__print_state('get_play_order')
        return self._gconf.get_string(PLAY_ORDER_KEY)
    
    
    def set_play_order(self, play_order):
        self.__print_state('set_play_order')
        self._gconf.set_string(PLAY_ORDER_KEY, play_order)
    
    
    def toggle_shuffle(self):
        self.__print_state('toggle_shuffle')
        status = self.get_play_order()
        new_status = self._play_toggle_shuffle[status]
        self.set_play_order(new_status)
        
    
    def toggle_loop(self):
        self.__print_state('toggle_loop')
        order = self.get_play_order()
        new_order = ORDER_LINEAR
        if self._play_toggle_loop.has_key(order):
            new_order = self._play_toggle_loop[order]      
        self.set_play_order(new_order)
    

    def get_play_queue(self, queue_limit=100):
        self.__print_state('get_play_queue')
        self.info('Getting play queue')
        entries = []
        self._loop_query_model(func=entries.append, query_model=self._get_play_queue_model(), limit=queue_limit)
        return entries
    
    
    def enqueue(self, entry_ids):
        self.__print_state('enqueue')
        self.info('Adding entries %s to queue' % entry_ids)
        if type(entry_ids) is list:
            for entry_id in entry_ids:
                entry = self.load_entry(entry_id)
                if entry is None:
                    continue
                location = str(entry.location)
                self.debug('Enqueuing entry %s' % location)
                self._shell.add_to_queue(location)
        elif type(entry_ids) is int:
            entry = self.load_entry(entry_ids)
            if not entry is None:
                location = str(entry.location)
                self.debug('Enqueuing entry %s' % location)
                self._shell.add_to_queue(location)
                
        self._shell.props.queue_source.queue_draw()
        
    def dequeue(self, entry_ids):
        self.__print_state('dequeue')
        if type(entry_ids) is list:
            self.info('Removing entries %s from queue' % entry_ids)
            for entry_id in entry_ids:
                entry = self.load_entry(entry_id)
                if entry is None:
                    continue
                location = str(entry.location)
                self.debug('Dequeuing entry %s' % location)
                self._shell.remove_from_queue(location)
        elif type(entry_ids) is int:
            self.info('Removing entry %d from queue' % entry_ids)
            entry = self.load_entry(entry_ids)
            if not entry is None:
                location = str(entry.location)
                self.debug('Dequeuing entry %s' % location)
                self._shell.remove_from_queue(location)
                
        self._shell.props.queue_source.queue_draw()
        
    
    def clear_play_queue(self):
        self.__print_state('clear_play_queue')
        self._loop_query_model(func=self.dequeue, query_model=self._get_play_queue_model())

    
    def _get_entry(self, entry_id):
        self.__print_state('get_entry')
        if not str(entry_id).isdigit():
            raise Exception('entry_id parameter must be an int')
        
        entry_id = int(entry_id)
        
        self.debug('Getting entry %d' % entry_id)
        return self._db.entry_lookup_by_id(entry_id)
    
    def load_entry(self, entry_id):
        self.__print_state('load_entry')
        self.debug('Loading entry %s' % str(entry_id))
        entry = self._get_entry(entry_id)
        if entry is None:
            self.debug('Entry %s not found' % str(entry_id))
            return None
        
        return RBEntry(self._db, entry)
    

    def get_playing_time(self):
        self.__print_state('get_time_playing')
        return self._player.get_playing_time()
    
    
    def get_playing_time_string(self):
        self.__print_state('get_playing_time_string')
        return self._player.get_playing_time_string()
    
    
    def next(self):
        self.__print_state('next')
        if self.get_playing_status():
            self._player.do_next()
        
        
    def seek(self, seconds):
        self.__print_state('seek')
        self._player.seek(seconds)
        
        
    def previous(self):
        self.__print_state('previous')
        if self.get_playing_status():
            self._player.do_previous()
    
    
    def play_pause(self):
        self.__print_state('play_pause')
        self._player.playpause()
        
    
    def _loop_query_model(self, func, query_model, first=0, limit=0):
        self.debug('Loop query_model...')

        if func is None:
            raise Exception('Func cannot be None')
        if query_model is None:
            raise Exception('Query Model cannot be None')

        
        if first != 0:
            limit = limit + first
        
        index = 0
        count = 0
        for row in query_model:
            self.debug('Reading Row...')

            if index < first:
                index += + 1
                self.debug('Skipping row ')
                continue
            
            entry = self._get_entry_id(row)
            func(entry)
            count += 1
            
            index += 1
            if limit != 0 and index >= limit:
                break
        
        return count
    
    def _get_play_queue_model(self):
        return self._shell.props.queue_source.props.query_model
    
    
    def _get_entry_id(self, row):
        if row is None:
            raise Exception('Row cannot be None')
        
        entry = row[0]
        return self._db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
    
    
    def get_playlists(self):
        playlists = []
        # Sourcelistmodel: 0 is for Queue, Music, Radios, Podcasts and else, 1 is for playlists
        index = 0
        for playlist in self._shell.props.sourcelist_model[1].iterchildren():
            playlistsource = PlaylistSource(index, playlist)
            playlists.append(playlistsource)
            index+= 1
        return playlists
    
    
    def enqueue_playlist(self, playlist_index):
        self.__print_state('enqueue_playlist')
        self.info('Enqueuing playlist')
        
        if not type(playlist_index) is int:
            raise Exception('playlist_index parameter must be an int')
        
        playlist = self.get_playlist(playlist_index)
        if playlist is None:
            return 0

        return self._loop_query_model(func=self.enqueue, query_model=playlist.source.props.query_model)
        
    
    def get_playlist(self, playlist_index):
        self.__print_state('get_playlist')
        self.info('Getting playlist')
        
        if not type(playlist_index) is int:
            raise Exception('playlist_index parameter must be an int')
        
        index = 0
        for playlist in self._shell.props.sourcelist_model[1].iterchildren():
            if playlist_index == index:
                return PlaylistSource(index, playlist)
            index += 1
            
        return None

    
    def get_playlist_entries(self, playlist_index, limit=100):
        self.__print_state('get_playlist_entries')
        self.info('Getting playlist entries')

        if not type(playlist_index) is int:
            raise Exception('playlist_index parameter must be an int')
        
        entries = []
        playlist = self.get_playlist(playlist_index)
        if not playlist is None:
            self._loop_query_model(func=entries.append, \
                                   query_model=playlist.source.props.query_model, \
                                   limit=limit)
        return entries
    
    
        

        
        
class RBEntry():
    
    id = None
    artist = None
    album = None
    track_number = None
    title = None
    duration = None
    rating = None
    year = None
    genre = None
    play_count = None
    location = None
    bitrate = None
    last_played = None
    
    def __init__(self, db, entry):
        self.id = db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
        self.title = db.entry_get(entry, rhythmdb.PROP_TITLE)
        self.artist = db.entry_get(entry, rhythmdb.PROP_ARTIST)
        self.album = db.entry_get(entry, rhythmdb.PROP_ALBUM)
        self.track_number = db.entry_get(entry, rhythmdb.PROP_TRACK_NUMBER)
        self.duration = db.entry_get(entry, rhythmdb.PROP_DURATION)
        self.rating = db.entry_get(entry, rhythmdb.PROP_RATING)
        self.year = db.entry_get(entry, rhythmdb.PROP_YEAR)
        self.genre = db.entry_get(entry, rhythmdb.PROP_GENRE)
        self.play_count = db.entry_get(entry, rhythmdb.PROP_PLAY_COUNT)
        self.location = db.entry_get(entry, rhythmdb.PROP_LOCATION)
        self.bitrate = db.entry_get(entry, rhythmdb.PROP_BITRATE)
        self.last_played = db.entry_get(entry, rhythmdb.PROP_LAST_PLAYED)
        
        

RB_SOURCELIST_MODEL_COLUMN_PLAYING = 0
RB_SOURCELIST_MODEL_COLUMN_PIXBUF = 1
RB_SOURCELIST_MODEL_COLUMN_NAME = 2
RB_SOURCELIST_MODEL_COLUMN_SOURCE = 3
RB_SOURCELIST_MODEL_COLUMN_ATTRIBUTES = 4
RB_SOURCELIST_MODEL_COLUMN_VISIBILITY = 5
RB_SOURCELIST_MODEL_COLUMN_IS_GROUP = 6
RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY = 7


class PlaylistSource():
    
    
    def __init__(self, index, entry):
        self.index = index
        self.is_playing = entry[RB_SOURCELIST_MODEL_COLUMN_PLAYING]
        self.pixbuf = entry[RB_SOURCELIST_MODEL_COLUMN_PIXBUF]
        self.name = entry[RB_SOURCELIST_MODEL_COLUMN_NAME]
        self.source = entry[RB_SOURCELIST_MODEL_COLUMN_SOURCE]
        self.attributes = entry[RB_SOURCELIST_MODEL_COLUMN_ATTRIBUTES]
        self.visibility = entry[RB_SOURCELIST_MODEL_COLUMN_VISIBILITY]
        self.is_group = entry[RB_SOURCELIST_MODEL_COLUMN_IS_GROUP]
        self.group_category = entry[RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY]
    

        
class InvalidQueryException(Exception):
    
    
    
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
