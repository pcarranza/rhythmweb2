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
import sys

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


RB_SOURCELIST_MODEL_COLUMN_PLAYING = 0
RB_SOURCELIST_MODEL_COLUMN_PIXBUF = 1
RB_SOURCELIST_MODEL_COLUMN_NAME = 2
RB_SOURCELIST_MODEL_COLUMN_SOURCE = 3
RB_SOURCELIST_MODEL_COLUMN_ATTRIBUTES = 4
RB_SOURCELIST_MODEL_COLUMN_VISIBILITY = 5
RB_SOURCELIST_MODEL_COLUMN_IS_GROUP = 6
RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY = 7


class RBHandler(Loggable):
    '''
    Rhythmbox shell wrapper, provides player, queue, playlist, 
    artist/album/genre count cache and max instances 
    and some other functionallities
    '''
    
    __CACHE_ARTISTS = 'artists'
    __CACHE_GENRES = 'genres'
    __CACHE_ALBUMS = 'albums'
    __CACHE_MAX_ARTIST = 'max-artist'
    __CACHE_MAX_GENRE = 'max-genre'
    __CACHE_MAX_ALBUM = 'max-album'
    
    
    def __init__(self, shell):
        '''
        Creates a new rhythmbox handler, wrapping the RBShell object that gets 
        by parameter
        '''
        
        self.debug('Creating new RBHandler object')
        
        if shell is None:
            self.error('Setting shell object to None')
            raise Exception('Shell object cannot be null')
        else:
            self.debug('Setting shell object')
        
        self.__shell = shell
        self.__db = shell.props.db
        self.__player = shell.get_player()
        self.__gconf = gconf.client_get_default()
        self.__media_types = {}
        for type in [TYPE_SONG, TYPE_RADIO, TYPE_PODCAST]:
            rb_type = self.__db.entry_type_get_by_name(type)
            self.__media_types[type] = rb_type
        
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
        
        self.__db_cache = {
                           self.__CACHE_ARTISTS : {},
                           self.__CACHE_MAX_ARTIST : None,
                           self.__CACHE_ALBUMS : {},
                           self.__CACHE_MAX_ALBUM : None,
                           self.__CACHE_GENRES : {},
                           self.__CACHE_MAX_GENRE : None
                           }
        
        self.__db.connect('entry-added', self.__append_entry_to_cache)
        
        self.__playing_song = None
        self.__player.connect('playing-song-changed', self.__playing_song_changed)
        
        

        
    def get_biggest_artist(self):
        '''
        Gets the artist that has more songs registered in the DB
        @return: a (name, value) tuple
        '''
        max_artist = self.__db_cache[self.__CACHE_MAX_ARTIST]
        return (max_artist, self.__db_cache[self.__CACHE_ARTISTS][max_artist]) 


    def get_biggest_album(self):
        '''
        Gets the album that has more songs registered in the DB
        @return: a (name, value) tuple
        '''
        max_album = self.__db_cache[self.__CACHE_MAX_ALBUM]
        return (max_album, self.__db_cache[self.__CACHE_ALBUMS][max_album])
    

    def get_biggest_genre(self):
        '''
        Gets the genre that has more songs registered in the DB
        @return: a (name, value) tuple
        '''
        max_genre = self.__db_cache[self.__CACHE_MAX_GENRE]
        return (max_genre, self.__db_cache[self.__CACHE_GENRES][max_genre])
        
        
    def get_artists(self):
        '''
        Gets the artists cached dictionary
        '''
        return self.__db_cache[self.__CACHE_ARTISTS]
    
    
    def get_albums(self):
        '''
        Gets the albums cached dictionary
        '''
        return self.__db_cache[self.__CACHE_ALBUMS]
    
    
    def get_genres(self):
        '''
        Gets the genres cached dictionary
        '''
        return self.__db_cache[self.__CACHE_GENRES]
    
        
    def get_playing_status(self):
        '''
        Gets the playing status, returns True or False according to playing or not
        '''
        return self.__player.get_playing() 
    
    
    def get_mute(self):
        '''
        Gets True if the player is muted
        '''
        return self.__player.get_mute()
    
    
    def toggle_mute(self):
        self.__player.toggle_mute()
        
        
    def get_volume(self):
        '''
        Gets the player volume, a float between 0 and 1
        '''
        return self.__player.get_volume()
    
        
    def set_volume(self, volume):
        '''
        Sets the player volume, gets a float between 0 and 1
        '''
        if not type(volume) is float:
            raise Exception('Volume must be a float')
        
        if volume > 1:
            self.warning('Volume cannot be set over 1')
            
        self.__player.set_volume(volume)
        
        
    def get_playing_entry_id(self):
        '''
        Gets playing entry id, returns a string
        '''
        entry = self.__player.get_playing_entry()
        if entry is None:
            return None
        
        return self.__db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
    
        
    def get_playing_time(self):
        '''
        Gets the playing time, in seconds
        '''
        return self.__player.get_playing_time()
    
    
    def get_playing_time_string(self):
        '''
        Gets the playing time, as a string in "x:xx of x:xx" format
        '''
        return self.__player.get_playing_time_string()
    
    
    def next(self):
        '''
        If playing, skips the player to the next song
        '''
        if self.get_playing_status():
            self.__player.do_next()
        
        
    def seek(self, seconds):
        '''
        Seeks n seconds in the current playing song, receives and int, positive or negative
        '''
        self.__player.seek(seconds)
        
        
    def previous(self):
        '''
        If playing, skips the player to the previous song
        '''
        if self.get_playing_status():
            self.__player.do_previous()
    
    
    def play_pause(self):
        '''
        Starts playing or pauses
        '''
        self.__player.playpause()
        
    
    def get_play_order(self):
        '''
        Returns the play order
        '''
        return self.__gconf.get_string(PLAY_ORDER_KEY)
    
    
    def set_play_order(self, play_order):
        '''
        Sets the play order
        '''
        self.__gconf.set_string(PLAY_ORDER_KEY, play_order)
    
    
    def toggle_shuffle(self):
        '''
        Toggles shuffle playing
        '''
        status = self.get_play_order()
        new_status = self._play_toggle_shuffle[status]
        self.set_play_order(new_status)
        
    
    def toggle_loop(self):
        '''
        Toggles loop playing
        '''
        order = self.get_play_order()
        new_order = ORDER_LINEAR
        if self._play_toggle_loop.has_key(order):
            new_order = self._play_toggle_loop[order]      
        self.set_play_order(new_order)
    

    def get_play_queue(self, queue_limit=100):
        '''
        Returns the play queue, limited to 100 entries by default
        '''
        self.info('Getting play queue')
        entries = []
        self.__loop_query_model(func=entries.append, query_model=self.__get_play_queue_model(), limit=queue_limit)
        return entries
    
    
    def play_entry(self, entry_id): # entry id
        '''
        Inmediatly starts playing the entry which id gets by parameter
        '''
        self.info('Playing entry %s' % entry_id)
        
        entry = self.__get_entry(entry_id)
        if not entry is None:
            if self.get_playing_status():
                self.play_pause()
            
            self.__player.play_entry(entry)
    
        
    def set_rating(self, entry_id, rating):
        '''
        Sets the provided rating to the given entry id, int 0 to 5 
        '''
        if not type(rating) is int:
            raise Exception('Rating parameter must be an int')
        
        self.info('Setting rating %d to entry %s' % (rating, entry_id))
        entry = self.__get_entry(entry_id)
        if not entry is None:
            self.__db.set(entry, rhythmdb.PROP_RATING, rating)
    
        
    def search_song(self, filter):
        '''
        Performs a query for entry type "song" with the provided filters 
        '''
        self.info('Searching for a song with filter %s' % filter)
        return self.search(filter, TYPE_SONG)
    
    
    def search_radio(self, filter):
        '''
        Performs a query for entry type "radio" with the provided filters 
        '''
        self.info('Searching for a radio with filter %s' % filter)
        return self.search(filter, TYPE_RADIO)
    
    
    def search_podcast(self, filter):
        '''
        Performs a query for entry type "podcast" with the provided filters 
        '''
        self.info('Searching for a podcast with filter %s' % filter)
        return self.search(filter, TYPE_PODCAST)
    
    
    def search(self, filter, type):
        '''
        Performs a query for provided entry type with the provided filters 
        '''
        filters = {}
        filters['type'] = type
        filters['all'] = filter
        
        return self.query(filters)
    
    
    def query(self, filters):
        '''
        Performs a query with the provided filters 
        '''
        self.debug('RBHandler.query...')
        if filters is None or not filters:
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
            for key in filters:
                value = filters[key]
                if type(value) is str:
                    self.debug('Searching for %s: "%s"' % (key, value))
                else:
                    self.warning('Searching for %s but type is "%s"' % (key, type(value)))
            
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
                self.debug('Appending query for type \"%s\"' % mtype)
                if not self.__media_types.has_key(mtype):
                    self.debug('Media \"%s\" not found' % mtype)
                    raise InvalidQueryException('Unknown media type \"%s\"' % mtype)
                else:
                    self.debug('Type %s added to query' % mtype)
            
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
            query_model = self.__query_all(mtype, play_count, rating, all, True)
              
        elif searches:
            self.info('Querying for each...')
            query_model = self.__query_all(mtype, play_count, rating, searches)
        
        elif mtype is None:
            self.info('No search filter defined, querying for default')
            query_model = self.__query_all(TYPE_SONG, play_count, rating, searches)
            
        else:
            self.info('Search for type only, querying for type')
            query_model = self.__query_all(mtype, play_count, rating, searches)

        self.debug('RBHandler.query executed, loading results...')
        entries = []
        self.__loop_query_model(func=entries.append, query_model=query_model, first=first, limit=limit)
        self.debug('RBHandler.query executed, returning results...')
        return entries
    
    
    def enqueue(self, entry_ids):
        '''
        Appends the given entry id or ids to the playing queue 
        '''
        self.info('Adding entries %s to queue' % entry_ids)
        if type(entry_ids) is list:
            for entry_id in entry_ids:
                entry = self.load_entry(entry_id)
                if entry is None:
                    continue
                location = str(entry.location)
                self.debug('Enqueuing entry %s' % location)
                self.__shell.add_to_queue(location)
        elif type(entry_ids) is int:
            entry = self.load_entry(entry_ids)
            if not entry is None:
                location = str(entry.location)
                self.debug('Enqueuing entry %s' % location)
                self.__shell.add_to_queue(location)
                
        self.__shell.props.queue_source.queue_draw()
        
        
    def dequeue(self, entry_ids):
        '''
        Removes the given entry id or ids from the playing queue 
        '''
        if type(entry_ids) is list:
            self.info('Removing entries %s from queue' % entry_ids)
            for entry_id in entry_ids:
                entry = self.load_entry(entry_id)
                if entry is None:
                    continue
                location = str(entry.location)
                self.debug('Dequeuing entry %s' % location)
                self.__shell.remove_from_queue(location)
        elif type(entry_ids) is int:
            self.info('Removing entry %d from queue' % entry_ids)
            entry = self.load_entry(entry_ids)
            if not entry is None:
                location = str(entry.location)
                self.debug('Dequeuing entry %s' % location)
                self.__shell.remove_from_queue(location)
                
        self.__shell.props.queue_source.queue_draw()
        
    
    def clear_play_queue(self):
        '''
        Cleans the playing queue
        '''
        self.__loop_query_model(func=self.dequeue, query_model=self.__get_play_queue_model())

    
    def load_entry(self, entry_id):
        '''
        Returns a RBEntry with the entry information fully loaded for the given id 
        '''
        self.debug('Loading entry %s' % str(entry_id))
        entry = self.__get_entry(entry_id)
        if entry is None:
            self.debug('Entry %s not found' % str(entry_id))
            return None
        
        return RBEntry(self.__db, entry)
    

    def get_playlists(self):
        '''
        Returns all registered playlists 
        '''
        playlists = []
        index = 0
        sources = self.__get_playlist_sources()
        for playlist in sources:
            playlistsource = PlaylistSource(index, playlist)
            playlists.append(playlistsource)
            index+= 1
        
        
        return playlists
    
    
    def enqueue_playlist(self, playlist_index):
        '''
        Enqueues in the play queue the given playlist 
        '''
        self.info('Enqueuing playlist')
        
        if not type(playlist_index) is int:
            raise Exception('playlist_index parameter must be an int')
        
        playlist = self.get_playlist(playlist_index)
        if playlist is None:
            return 0
        
        # playlist.add_to_queue(self.__shell.props.queue_source)
        # This way we will know how many songs are added
        return self.__loop_query_model(func=self.enqueue, query_model=playlist.source.props.query_model)
        
    
    def get_playlist(self, playlist_index):
        '''
        Returns the playlist required by index 
        '''
        self.info('Getting playlist')
        
        if not type(playlist_index) is int:
            raise Exception('playlist_index parameter must be an int')
        
        index = 0
        sources = self.__get_playlist_sources()
        for playlist in sources:
            if playlist_index == index:
                return PlaylistSource(index, playlist)
            index += 1
            
        return None

    
    def get_playlist_entries(self, playlist_index, limit=100):
        '''
        Returns every entry id registered in a given playlist 
        '''
        self.info('Getting playlist entries')

        if not type(playlist_index) is int:
            raise Exception('playlist_index parameter must be an int')
        
        entries = []
        playlist = self.get_playlist(playlist_index)
        if not playlist is None:
            self.__loop_query_model(func=entries.append, \
                                   query_model=playlist.source.props.query_model, \
                                   limit=limit)
        return entries


    def __append_entry_to_cache(self, db, entry):
        '''
        Appends the given entry to the rbhandler cache 
        '''
        entry_id = db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
        artist = db.entry_get(entry, rhythmdb.PROP_ARTIST)
        album = db.entry_get(entry, rhythmdb.PROP_ALBUM)
        genre = db.entry_get(entry, rhythmdb.PROP_GENRE)
        play_count = db.entry_get(entry, rhythmdb.PROP_PLAY_COUNT)
        
        if not artist:
            self.debug('Empty artist for entry %d %s, skipping' % (entry_id, db.entry_get(entry, rhythmdb.PROP_LOCATION)))
            return
        
        if not album:
            self.debug('Empty album for entry %d %s, skipping' % (entry_id, db.entry_get(entry, rhythmdb.PROP_LOCATION)))
            return
        
        if not genre:
            self.debug('Empty genre for entry %d %s, skipping' % (entry_id, db.entry_get(entry, rhythmdb.PROP_LOCATION)))
            return

        if not play_count:
            play_count = 0
        
        self.__append_artist(artist, play_count)
        self.__append_album(album, play_count)
        self.__append_genre(genre, play_count)
    
    def __append_artist(self, artist, play_count):
        self.debug('Append playcount in %d to artist "%s"' % (play_count, artist))    
        artists_cache = self.__db_cache[self.__CACHE_ARTISTS]
        
        if artists_cache.has_key(artist):
            artists_cache[artist] += play_count
        else:
            artists_cache[artist] = play_count
            
        if self.__db_cache[self.__CACHE_MAX_ARTIST] is None:
            self.__db_cache[self.__CACHE_MAX_ARTIST] = artist
        elif artists_cache[artist] > artists_cache[self.__db_cache[self.__CACHE_MAX_ARTIST]]:
            self.__db_cache[self.__CACHE_MAX_ARTIST] = artist
            
    
    def __append_album(self, album, play_count):
        self.debug('Append playcount in %d to album "%s"' % (play_count, album))
        albums_cache = self.__db_cache[self.__CACHE_ALBUMS]
        
        if albums_cache.has_key(album):
            albums_cache[album] += play_count
        else:
            albums_cache[album] = play_count

        if self.__db_cache[self.__CACHE_MAX_ALBUM] is None:
            self.__db_cache[self.__CACHE_MAX_ALBUM] = album
        elif albums_cache[album] > albums_cache[self.__db_cache[self.__CACHE_MAX_ALBUM]]:
            self.__db_cache[self.__CACHE_MAX_ALBUM] = album


    def __append_genre(self, genre, play_count):
        self.debug('Append playcount in %d to genre "%s"' % (play_count, genre))
        genres_cache = self.__db_cache[self.__CACHE_GENRES]
    
        if genres_cache.has_key(genre):
            genres_cache[genre] += play_count
        else:
            genres_cache[genre] = play_count

        if self.__db_cache[self.__CACHE_MAX_GENRE] is None:
            self.__db_cache[self.__CACHE_MAX_GENRE] = genre
        elif genres_cache[genre] > genres_cache[self.__db_cache[self.__CACHE_MAX_GENRE]]:
            self.__db_cache[self.__CACHE_MAX_GENRE] = genre
    
    
    def __playing_song_changed(self, player, entry):
        self.debug('Playing song changed....')
        if not self.__playing_song is None:
            old_playcount = self.__playing_song.play_count
            old_entry = self.__get_entry(self.__playing_song.id)
            new_play_count = self.__db.entry_get(old_entry, rhythmdb.PROP_PLAY_COUNT)
            if old_playcount < new_play_count:
                diff = new_play_count - old_playcount
                self.__append_artist(self.__playing_song.artist, diff)
                self.__append_album(self.__playing_song.album, diff)
                self.__append_genre(self.__playing_song.genre, diff)
                
        if entry is None:
            self.__playing_song = None
        else:
            self.__playing_song = RBEntry(self.__db, entry)
            
    

    def __query_all(self, mtype, min_play_count, min_rating, parameters, query_for_all=False):
        '''
        Performs the quey
        '''
        self.info('Querying...')
        db = self.__db
        if mtype == TYPE_SONG:
            query_model = db.query_model_new(\
                     db.query_new(), \
                     rhythmdb.rhythmdb_query_model_track_sort_func, \
                     0, \
                     db.query_model_new_empty())
        else:
            query_model = db.query_model_new_empty()
        
        if mtype is None:
            type = None
        else:
            type = (rhythmdb.QUERY_PROP_EQUALS, \
                rhythmdb.PROP_TYPE, \
                self.__db.entry_type_get_by_name(mtype))
        
        
        if query_for_all: # equivalent to use an OR (many queries)
            self.info('Query for all parameters separatedly')
            for parameter in parameters:
                self.info('Appending Query for parameter...')
                query = db.query_new()
                if not type is None:
                    self.info('Appending Query for type \"%s\"...' % mtype)
                    db.query_append(query, type)
                self.__append_rating_query(query, min_rating)
                self.__append_play_count_query(query, min_play_count)
                db.query_append(query, parameter)
                db.do_full_query_parsed(query_model, query)
        else:
            self.info('Query for all parameters in one only full search')
            query = db.query_new()
            if not type is None:
                self.info('Appending Query for type \"%s\"...' % mtype)
                db.query_append(query, type)
            self.__append_rating_query(query, min_rating)
            self.__append_play_count_query(query, min_play_count)
            for parameter in parameters:
                self.info('Appending Query for parameter...')
                db.query_append(query, parameter)
            db.do_full_query_parsed(query_model, query)
            
        return query_model
    
    
    def __append_play_count_query(self, query, play_count):
        '''
        Appends a min playcount filter to the given query
        '''
        if play_count > 0:
            self.info('Appending min play count %d' % play_count)
            db = self.__db
            play_count_query = (rhythmdb.QUERY_PROP_GREATER, \
                rhythmdb.PROP_PLAY_COUNT, \
                play_count)
            db.query_append(query, play_count_query)


    def __append_rating_query(self, query, rating):
        '''
        Appends a min rating filter to the given query
        '''
        if rating > 0:
            self.info('Appending min rating %d' % rating)
            db = self.__db
            rating_query = (rhythmdb.QUERY_PROP_GREATER, \
                rhythmdb.PROP_RATING, \
                rating)
            db.query_append(query, rating_query)
    
    
    def __get_play_queue_model(self):
        '''
        Returns the main play queue query model
        '''
        return self.__shell.props.queue_source.props.query_model
    
    
    def __get_entry_id(self, row):
        '''
        Returns the entry id for a given row from a query model
        '''
        if row is None:
            raise Exception('Row from query model cannot be None')
        
        entry = row[0]
        return self.__db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
    
    
    def __get_playlist_sources(self):
        '''
        Returns a list with all playlists sources registered
        '''
        playlists = []
        for sourcelist in self.__shell.props.sourcelist_model:
            if sourcelist[RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY] == rb.SOURCE_GROUP_CATEGORY_PERSISTENT:
                for playlist in sourcelist.iterchildren():
                    playlists.append(playlist)
        return playlists
    
        
    def __loop_query_model(self, func, query_model, first=0, limit=0):
        '''
        Loops a query model object and invokes the given function for every row, can also receive a first and a limit to "page" 
        '''
        
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
            
            entry = self.__get_entry_id(row)
            func(entry)
            count += 1
            
            index += 1
            if limit != 0 and index >= limit:
                break
        
        return count
    
    
    def __get_entry(self, entry_id):
        '''
        Returns an entry by its id
        '''
        if not str(entry_id).isdigit():
            raise Exception('entry_id parameter must be an int')
        
        entry_id = int(entry_id)
        
        self.debug('Getting entry %d' % entry_id)
        return self.__db.entry_lookup_by_id(entry_id)
    
    

        
        
class RBEntry():
    '''
    Rhythmbox entry wrapper, loads all entry data on initialization
    '''
    
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
        
        

class PlaylistSource():
    '''
    Playlist source wrapper, loads all data on initialization
    '''
    
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
