import random
import logging
log = logging.getLogger(__name__)

from gi.repository import RB, GLib

ORDER_LINEAR = 'linear'
ORDER_SHUFFLE = 'shuffle'
ORDER_SHUFFLE_BY_AGE_AND_RATING = 'random-by-age-and-rating'
ORDER_SHUFFLE_BY_AGE = 'random-by-age'
ORDER_SHUFFLE_BY_RATING = 'random-by-rating'
ORDER_SHUFFLE_EQUALS = 'random-equal-weights'

PLAY_ORDER_KEY = '/apps/rhythmbox/state/play_order'
PLAY_LOOP = '-loop'

TYPE_SONG = 'song'
TYPE_RADIO = 'iradio'
TYPE_PODCAST = 'podcast-post'

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


class RBHandler(object):
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
        if not shell:
            raise Exception('Shell object cannot be null')

        log.debug('Setting shell object')
        
        self.shell = shell
        self.player = shell.props.shell_player
        self.db = shell.props.db

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
        
        self.__media_types = {}
        for t in [TYPE_SONG, TYPE_RADIO, TYPE_PODCAST]:
            rb_type = self.db.entry_type_get_by_name(t)
            self.__media_types[t] = rb_type

        log.debug('rbhandler loaded')

    def get_playing_status(self):
        '''
        Gets the playing status, returns True or False according to playing or not
        '''
        log.debug('get playing status')
        return self.player.get_playing()[1]
    
    def get_mute(self):
        '''
        Gets True if the player is muted
        '''
        log.debug('get mute status')
        return self.player.get_mute()[1]
    
    def toggle_mute(self):
        log.debug('toggle mute')
        self.player.toggle_mute()
        
    def get_volume(self):
        '''
        Gets the player volume, a float between 0 and 1
        '''
        log.debug('get volume')
        return self.player.get_volume()[1]
        
    def set_volume(self, volume):
        '''
        Sets the player volume, gets a float between 0 and 1
        '''
        if not type(volume) is float:
            raise Exception('Volume must be a float')
        
        log.debug('set volume %d' % volume)
        
        if volume > 1:
            log.warning('Volume cannot be set over 1')
            
        self.player.set_volume(volume)
    
    def get_playing_entry_id(self):
        '''
        Gets playing entry id, returns a string
        '''
        entry = self.get_playing_entry()
        if entry is None:
            return None
        
        return self.get_entry_id(entry)
    
    def get_playing_entry(self):
        '''
        Returns the rhythmbox current playing entry object
        '''
        log.debug('get playing entry')
        return self.player.get_playing_entry()
    
    def get_playing_time(self):
        '''
        Gets the playing time, in seconds
        '''
        log.debug('get playing time')
        return self.player.get_playing_time()[1]
    
    def get_playing_time_string(self):
        '''
        Gets the playing time, as a string in "x:xx of x:xx left" format
        '''
        log.debug('get playing time string')
        return self.player.get_playing_time_string()
    
    def play_next(self):
        '''
        If playing, skips the player to the next song
        '''
        log.debug('skip to next')
        if self.get_playing_status():
            self.player.do_next()
        
    def seek(self, seconds):
        '''
        Seeks n seconds in the current playing song, receives and int, positive or negative
        '''
        log.debug('seek %d seconds' % seconds)
        self.player.seek(seconds)
        
    def previous(self):
        '''
        If playing, skips the player to the previous song
        '''
        log.debug('skip to previous')
        if self.get_playing_status():
            self.player.do_previous()
    
    def play_pause(self):
        '''
        Starts playing or pauses
        '''
        log.debug('toggle playing status')
        
        status = self.get_playing_status()
        return self.player.playpause(not status)
    
    def play_entry(self, entry_id): # entry id
        '''
        Inmediatly starts playing the entry which id gets by parameter
        '''
        log.info('Playing entry %s' % entry_id)
        
        entry = self.get_entry(entry_id)
        if not entry is None:
            self._play_entry(entry)
    
    def _play_entry(self, entry):
        '''
        Inmediately starts playing provided entry
        '''
        log.debug('play entry %s' % entry)
        if entry is None:
            return

        if self.get_playing_status():
            self.play_pause()
        
        playing_source = self.player.get_playing_source()
        if not self.player.get_playing_source():
            playing_source = self.player.props.queue_source
        self.player.play_entry(entry, playing_source)
    
    def get_play_order(self):
        '''
        Returns the play order
        '''
        return self.player.props.play_order
    
    def set_play_order(self, play_order):
        '''
        Sets the play order
        '''
        self.player.props.play_order = play_order
    
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
        if order in self._play_toggle_loop:
            new_order = self._play_toggle_loop[order]
        self.set_play_order(new_order)

#    def playing_song_changed(self, player, entry):
#        log.debug('Playing song changed....')
#        if not self.__playing_song is None:
#            old_playcount = self.__playing_song.play_count
#            old_entry = self.get_entry(self.__playing_song.id)
#            new_play_count = self.get_value(old_entry, RB.RhythmDBPropType.PLAY_COUNT)
#            if old_playcount < new_play_count:
#                diff = new_play_count - old_playcount
#                self.__append_artist(self.__playing_song.artist, diff)
#                self.__append_album(self.__playing_song.album, diff)
#                self.__append_genre(self.__playing_song.genre, diff)
#                
#        if entry is None:
#            self.__playing_song = None
#        else:
#            self.__playing_song = self.load_rb_entry(entry)

    # QUEUE
    def get_play_queue(self, queue_limit=100):
        '''
        Returns the play queue, limited to 100 entries by default
        '''
        log.info('Getting play queue')
        entries = []
        self.loop_query_model(func=entries.append, 
                query_model=self.get_play_queue_model(), 
                limit=queue_limit)
        log.debug('Returning entries list {}'.format(entries))
        return entries
    
    def get_play_queue_model(self):
        '''
        Returns the main play queue query model
        '''
        return self.shell.props.queue_source.props.query_model
    
    def clear_play_queue(self):
        '''
        Cleans the playing queue
        '''
        self.loop_query_model(func=self.dequeue, query_model=self.get_play_queue_model())
    
    def shuffle_queue(self):
        log.debug('shuffling queue')
        entries = self.get_play_queue()
        if entries:
            log.debug('There are entries, actually shuffling the queue')
            random.shuffle(entries)
            
            for i in range(0, len(entries)):
                log.info('Moving entry {} to {}'.format(entries[i].id, i))
                entry = self.shell.props.db.entry_lookup_by_id(entries[i].id)
                self.move_entry_in_queue(entry, i)
    
    def move_entry_in_queue(self, entry, index):
        queue = self.shell.props.queue_source
        queue.move_entry(entry, index)
    
    def enqueue(self, entry_ids):
        '''
        Appends the given entry id or ids to the playing queue 
        '''
        log.info('Adding entries %s to queue' % entry_ids)
        if type(entry_ids) is list:
            for entry_id in entry_ids:
                entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
                if entry is None:
                    continue
                self.shell.props.queue_source.add_entry(entry, -1)

        elif type(entry_ids) is int:
            entry = self.shell.props.db.entry_lookup_by_id(int(entry_ids))
            if not entry is None:
                self.shell.props.queue_source.add_entry(entry, -1)
        else:
            log.info('Plain RBEntry')
            entry = self.shell.props.db.entry_lookup_by_id(entry_ids.id)
            self.shell.props.queue_source.add_entry(entry, -1)

        self.shell.props.queue_source.queue_draw()
        
        
    def dequeue(self, entry_ids):
        '''
        Removes the given entry id or ids from the playing queue 
        '''
        if type(entry_ids) is list:
            log.info('Removing entries %s from queue' % entry_ids)
            for entry_id in entry_ids:
                entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
                if entry is None:
                    continue
                self.shell.props.queue_source.remove_entry(entry)
        elif type(entry_ids) is int:
            log.info('Removing entry %d from queue' % entry_ids)
            entry = self.shell.props.db.entry_lookup_by_id(int(entry_ids))
            if not entry is None:
                self.shell.props.queue_source.remove_entry(entry)
                
        self.shell.props.queue_source.queue_draw()

    # ENTRY
    def get_entry(self, entry_id):
        '''
        Returns an entry by its id
        '''
        if not str(entry_id).isdigit():
            raise Exception('entry_id parameter must be an int')
        
        entry_id = int(entry_id)
        
        log.debug('Getting entry %d' % entry_id)
        return self.db.entry_lookup_by_id(entry_id)
       
    def load_entry(self, entry):
        '''
        Returns a RBEntry with the entry information fully loaded for the given id 
        '''
        if entry is None:
            log.info('Entry is None')
            return None
        
        rbentry = RBEntry()
        rbentry.id = entry.get_ulong(RB.RhythmDBPropType.ENTRY_ID)
        rbentry.title = entry.get_string(RB.RhythmDBPropType.TITLE) # self.get_value(entry, RB.RhythmDBPropType.TITLE)
        rbentry.artist = entry.get_string(RB.RhythmDBPropType.ARTIST) # self.get_value(entry, RB.RhythmDBPropType.ARTIST)
        rbentry.album = entry.get_string(RB.RhythmDBPropType.ALBUM)
        rbentry.track_number = entry.get_ulong(RB.RhythmDBPropType.TRACK_NUMBER)
        rbentry.duration = entry.get_ulong(RB.RhythmDBPropType.DURATION)
        rbentry.rating = entry.get_double(RB.RhythmDBPropType.RATING)
        rbentry.year = entry.get_ulong(RB.RhythmDBPropType.YEAR)
        rbentry.genre = entry.get_string(RB.RhythmDBPropType.GENRE)
        rbentry.play_count = entry.get_ulong(RB.RhythmDBPropType.PLAY_COUNT)
        rbentry.location = entry.get_string(RB.RhythmDBPropType.LOCATION)
        rbentry.bitrate = entry.get_ulong(RB.RhythmDBPropType.BITRATE)
        rbentry.last_played = entry.get_ulong(RB.RhythmDBPropType.LAST_PLAYED)

        log.debug('Entry {} loaded'.format(rbentry.id))

        return rbentry
        
    def load_rb_entry(self, entry_id):
        '''
        Returns a RBEntry with the entry information fully loaded for the given id 
        '''
        log.debug('Loading entry %s' % str(entry_id))
        entry = self.get_entry(entry_id)
        if entry is None:
            log.info('Entry %s not found' % str(entry_id))
            return None
       
        return self.load_entry(entry)
    
    
    def set_rating(self, entry_id, rating):
        '''
        Sets the provided rating to the given entry id, int 0 to 5 
        '''
        if not type(rating) is int:
            raise Exception('Rating parameter must be an int')
        
        log.info('Setting rating %d to entry %s' % (rating, entry_id))
        entry = self.get_entry(entry_id)
        if not entry is None:
            self.db.entry_set(entry, RB.RhythmDBPropType.RATING, rating)
    
    def get_entry_id(self, entry):
        return entry.get_ulong(RB.RhythmDBPropType.ENTRY_ID)

    # MODEL
    def loop_query_model(self, func, query_model, first=0, limit=0):
        '''
        Loops a query model object and invokes the given function for every row, can also receive a first and a limit to "page" 
        '''
        log.debug('Loop query_model...')

        if func is None:
            raise Exception('Func cannot be None')
        if query_model is None:
            raise Exception('Query Model cannot be None')
        
        if first != 0:
            limit = limit + first
        
        index = 0
        count = 0
        for row in query_model:
            if index < first:
                log.debug('Skipping row {}'.format(index))
                index += 1
                continue
            
            log.debug('Reading Row {}...'.format(index))
            entry = self.get_entry_from_row(row)
            entry_id = self.load_entry(entry)
            
            func(entry_id)
            count += 1
            
            index += 1
            if limit != 0 and index >= limit:
                break
        return count
    
    def get_entry_from_row(self, row):
        '''
        Returns the entry id for a given row from a query model
        '''
        if row is None:
            raise Exception('Row from query model cannot be None')
        
        return row[0]

    # Query
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
        self.loop_query_model(func=entries.append, query_model=query_model, first=first, limit=limit)
        log.debug('RBHandler.query executed, returning results...')
        return entries

    # SOURCE
    def play_source(self, source):
        log.info('Set source playing')
        if self.get_playing_status():
            self.play_pause()
        self.shell.props.shell_player.set_playing_source(source.source)
        return self.play_pause()
    
    def get_source(self, source_index):
        log.info('Getting source with index %d' % source_index)
        
        if not type(source_index) is int:
            raise Exception('source_index parameter must be an int')
        index = 0
        sources = self.get_sources()
        for source in sources:
            if source.index == source_index:
                log.debug('Returning source with index %d' % index)
                return source
            index += 1
        return None
        
    def get_source_entries(self, source, limit=100):
        log.info('Getting source entries')
        entries = []
        if not source is None:
            self.loop_query_model(func=entries.append,
                                   query_model=source.query_model,
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
        return []
    
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
        return self.loop_query_model(
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

class InvalidQueryException(Exception):
    
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class RBEntry(object):
    '''
    Rhythmbox entry wrapper, loads all entry data on initialization
    '''
    def __init__(self):
        self.id = None
        self.artist = None
        self.album = None
        self.track_number = None
        self.title = None
        self.duration = None
        self.rating = None
        self.year = None
        self.genre = None
        self.play_count = None
        self.location = None
        self.bitrate = None
        self.last_played = None

