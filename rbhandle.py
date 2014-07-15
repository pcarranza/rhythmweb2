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
    """
    Rhythmbox shell wrapper, provides player, queue, playlist,
    artist/album/genre count cache and max instances
    and some other functionallities
    """

    def __init__(self, shell):
        """
        Creates a new rhythmbox handler, wrapping the RBShell object that gets
        by parameter
        """
        if not shell:
            raise Exception('Shell object cannot be null')

        log.debug('Setting shell object')

        self.shell = shell
        self.player = shell.props.shell_player
        self.db = shell.props.db

        LINEAR_LOOP = "%s%s" % (ORDER_LINEAR, PLAY_LOOP)
        SHUFFLE_LOOP = "%s%s" % (ORDER_SHUFFLE, PLAY_LOOP)

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

        self.media_types = {}
        for entry_type in [TYPE_SONG, TYPE_RADIO, TYPE_PODCAST]:
            rb_type = self.db.entry_type_get_by_name(entry_type)
            self.media_types[entry_type] = rb_type
        log.debug('rbhandler loaded')

    def get_playing_status(self):
        """Gets the playing status, returns True or False according to playing or not"""
        return self.player.get_playing()[1]

    def get_mute(self):
        """Gets True if the player is muted"""
        return self.player.get_mute()[1]

    def toggle_mute(self):
        self.player.toggle_mute()

    def get_volume(self):
        """Gets the player volume, a float between 0 and 1"""
        log.debug('get volume')
        return self.player.get_volume()[1]

    def set_volume(self, volume):
        """Sets the player volume, gets a float between 0 and 1"""
        if not type(volume) is float:
            raise Exception('Volume must be a float')
        log.debug('set volume %d' % volume)
        if volume > 1:
            log.warning('Volume cannot be set over 1')

        self.player.set_volume(volume)

    def get_playing_entry_id(self):
        """Gets playing entry id, returns a string"""
        entry = self.get_playing_entry()
        if entry is None:
            return None

        return self.get_entry_id(entry)

    def get_entry_id(self, entry):
        return entry.get_ulong(RB.RhythmDBPropType.ENTRY_ID)

    def get_playing_entry(self):
        """Returns the rhythmbox current playing entry object"""
        return self.player.get_playing_entry()

    def get_playing_time(self):
        """Gets the playing time, in seconds"""
        return self.player.get_playing_time()[1]

    def get_playing_time_string(self):
        """Gets the playing time, as a string in "x:xx of x:xx left" format"""
        return self.player.get_playing_time_string()

    def play_next(self):
        """If playing, skips the player to the next song"""
        log.debug('skip to next')
        if self.get_playing_status():
            self.player.do_next()

    def seek(self, seconds):
        """Seeks n seconds in the current playing song, receives and int, positive or negative"""
        log.debug('seek %d seconds' % seconds)
        self.player.seek(seconds)

    def previous(self):
        """If playing, skips the player to the previous song"""
        if self.get_playing_status():
            self.player.do_previous()

    def play_pause(self):
        """Starts playing or pauses"""
        status = self.get_playing_status()
        return self.player.playpause(not status)

    def play_entry(self, entry_id): # entry id
        """Inmediatly starts playing the entry which id gets by parameter"""
        entry = self.get_entry(entry_id)
        if entry is None:
            return
        if self.get_playing_status():
            self.play_pause()
        playing_source = self.player.get_playing_source()
        if not self.player.get_playing_source():
            playing_source = self.player.props.queue_source
        self.player.play_entry(entry, playing_source)

    def get_play_order(self):
        """Returns the play order"""
        return self.player.props.play_order

    def set_play_order(self, play_order):
        """Sets the play order"""
        self.player.props.play_order = play_order

    def toggle_shuffle(self):
        """Toggles shuffle playing"""
        status = self.get_play_order()
        new_status = self._play_toggle_shuffle[status]
        self.set_play_order(new_status)

    def toggle_loop(self):
        """Toggles loop playing"""
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
        """Returns the play queue, limited to 100 entries by default"""
        entries = []
        self.loop_query_model(func=entries.append,
                query_model=self.get_play_queue_model(),
                limit=queue_limit)
        return entries

    def get_play_queue_model(self):
        """Returns the main play queue query model"""
        return self.shell.props.queue_source.props.query_model

    def clear_play_queue(self):
        """Cleans the playing queue"""
        self.loop_query_model(func=self.dequeue, query_model=self.get_play_queue_model())

    def shuffle_queue(self):
        entries = self.get_play_queue()
        if entries:
            random.shuffle(entries)
            queue = self.shell.props.queue_source
            for i in range(0, len(entries)):
                entry = self.shell.props.db.entry_lookup_by_id(entries[i].id)
                queue.move_entry(entry, i)

    def enqueue(self, entry_ids):
        """Appends the given entry id or ids to the playing queue"""
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
            entry = self.shell.props.db.entry_lookup_by_id(entry_ids.id)
            self.shell.props.queue_source.add_entry(entry, -1)
        self.shell.props.queue_source.queue_draw()

    def dequeue(self, entry_ids):
        """Removes the given entry id or ids from the playing queue"""
        if type(entry_ids) is list:
            for entry_id in entry_ids:
                entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
                if entry is None:
                    continue
                self.shell.props.queue_source.remove_entry(entry)
        elif type(entry_ids) is int:
            entry = self.shell.props.db.entry_lookup_by_id(int(entry_ids))
            if not entry is None:
                self.shell.props.queue_source.remove_entry(entry)
        self.shell.props.queue_source.queue_draw()

    # ENTRY
    def get_entry(self, entry_id):
        """Returns an entry by its id"""
        if not str(entry_id).isdigit():
            raise Exception('entry_id parameter must be an int')
        entry_id = int(entry_id)
        return self.db.entry_lookup_by_id(entry_id)

    def load_entry(self, entry):
        """Returns a RBEntry with the entry information fully loaded for the given id"""
        if entry is None:
            return None
        return RBEntry(entry)

    def set_rating(self, entry_id, rating):
        """Sets the provided rating to the given entry id, int 0 to 5"""
        if not type(rating) is int:
            raise Exception('Rating parameter must be an int')
        entry = self.get_entry(entry_id)
        if not entry is None:
            self.db.entry_set(entry, RB.RhythmDBPropType.RATING, rating)

    def loop_query_model(self, func, query_model, first=0, limit=0):
        """Loops a query model object and invokes the given function for every row, can also receive a first and a limit to 'page'"""
        if func is None:
            raise ValueError('Function to call cannot be None')
        if query_model is None:
            raise ValueError('Query Model cannot be None')
        if first != 0:
            limit = limit + first
        index, count = 0, 0
        for row in query_model:
            if index < first:
                log.debug('Skipping row {}'.format(index))
                index += 1
                continue
            log.debug('Reading Row {}...'.format(index))
            entry = self.get_entry_from_row(row)
            rb_entry = self.load_entry(entry)

            func(rb_entry)
            count += 1
            index += 1
            if limit != 0 and index >= limit:
                break
        return count

    def get_entry_from_row(self, row):
        """Returns the entry id for a given row from a query model"""
        if row is None:
            raise ValueError('Row from query model cannot be None')
        return row[0]

    # Query
    def search_song(self, query):
        """Performs a query for entry type "song" with the provided query"""
        log.info('Searching for a song with query %s' % query)
        return self.search(query, TYPE_SONG)

    def search_radio(self, query):
        """Performs a query for entry type "radio" with the provided query"""
        log.info('Searching for a radio with filter %s' % query)
        return self.search(query, TYPE_RADIO)

    def search_podcast(self, query):
        """Performs a query for entry type "podcast" with the provided filters"""
        log.info('Searching for a podcast with filter %s' % query)
        return self.search(query, TYPE_PODCAST)

    def search(self, query, media_type):
        """Performs a query for provided entry type with the provided query and media type"""
        filters = {}
        filters['type'] = media_type
        filters['all'] = query
        return self.query(filters)

    def query(self, filters):
        """Performs a query with the provided filters"""
        log.debug('RBHandler.query...')
        if not filters:
            log.info('No filters, returning empty result')
            return []

        media_type = self.media_types[TYPE_SONG]
        rating, play_count, first, limit = 0, 0, 0, 0
        query = Query()

        if filters:
            for key in filters:
                value = filters[key]
                if type(value) is str:
                    log.debug('Searching for %s: "%s"' % (key, value))
                else:
                    log.warning('Searching for %s but type is "%s"' % (key, type(value)))

            if 'exact-match' in filters:
                query.matcher = RB.RhythmDBQueryType.EQUALS

            if 'first' in filters:
                try:
                    first = int(filters['first'])
                except:
                    raise InvalidQueryException('Parameter first must be a number, it actually is \"%s\"' % first)

            if 'limit' in filters:
                try:
                    limit = int(filters['limit'])
                except:
                    raise InvalidQueryException('Parameter limit must be a number, it actually is \"%s\"' % limit)

            if 'type' in filters:
                media_type = self.media_types.get(filters['type'], None)
                if not media_type:
                    raise InvalidQueryException('Unknown type {}'.format(filters['type']))

            if 'rating' in filters:
                try:
                    rating = float(filters['rating'])
                except:
                    raise InvalidQueryException('Parameter rating must be a float, it actually is \"%s\"' % rating)

            if 'play_count' in filters:
                try:
                    play_count = int(filters['play_count'])
                except:
                    raise InvalidQueryException('Parameter play_count must be an int, it actually is \"%s\"' % play_count)

            if 'all' in filters:
                query.add_all(filters['all'])
            else:
                query.add_artist(filters.get('artist', None))
                query.add_title(filters.get('title', None))
                query.add_album(filters.get('album', None))
                query.add_genre(filters.get('genre', None))
            query.add_type(media_type)
            query.add_rating(rating)
            query.add_play_count(play_count)

        query_model = query.execute(self.db)
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

    def load_source_entries(self, source, limit=100):
        if source is None:
            return
        entries = []
        self.loop_query_model(func=entries.append,
                                query_model=source.query_model,
                                limit=limit)
        source.entries = entries

    def get_playlists(self):
        """Returns all registered playlists"""
        sourcelist = self.shell.props.playlist_manager.get_playlists()
        sources = []
        for index, source in enumerate(sourcelist):
            sources.append(RBSource(index, source))
        return sources

    def get_sources(self):
        """Returns all fixed sources, disabled by now"""
        return []

    def enqueue_source(self, source):
        """Enqueues in the play queue the given playlist"""
        if not source:
            return 0
        # playlist.add_to_queue(self.shell.props.queue_source)
        # This way we will know how many songs are added
        return self.loop_query_model(
                   func=self.enqueue,
                   query_model=source.query_model)


class Query(object):

    def __init__(self):
        self.filters = []
        self.static_filters = []
        self.query_for_all = False
        self.matcher = RB.RhythmDBQueryType.FUZZY_MATCH
        self.sort_func = RB.RhythmDBQueryModel.album_sort_func

    def add_artist(self, artist):
        if not artist:
            return
        self.filters.append((self.matcher,
            RB.RhythmDBPropType.ARTIST_FOLDED,
            artist.lower()))

    def add_title(self, title):
        if not title:
            return
        self.filters.append((self.matcher,
            RB.RhythmDBPropType.TITLE_FOLDED,
            title.lower()))

    def add_album(self, album):
        if not album:
            return
        self.filters.append((self.matcher,
            RB.RhythmDBPropType.ALBUM_FOLDED,
            album.lower()))

    def add_genre(self, genre):
        if not genre:
            return
        self.filters.append((self.matcher,
            RB.RhythmDBPropType.GENRE_FOLDED,
            genre.lower()))

    def add_all(self, value):
        if not value:
            return
        self.add_artist(value)
        self.add_title(value)
        self.add_album(value)
        self.add_genre(value)
        self.query_for_all = True

    def add_type(self, media_type):
        self.static_filters.append((RB.RhythmDBQueryType.EQUALS,
            RB.RhythmDBPropType.TYPE,
            media_type))

    def add_play_count(self, play_count):
        if not play_count:
            return
        self.static_filters.append((RB.RhythmDBQueryType.GREATER_THAN,
            RB.RhythmDBPropType.PLAY_COUNT,
            play_count))

    def add_rating(self, rating):
        if not rating:
            return
        self.static_filters.append((RB.RhythmDBQueryType.GREATER_THAN,
            RB.RhythmDBPropType.RATING,
            rating))

    def execute(self, db):
        """Runs the query on the database"""
        query_model = RB.RhythmDBQueryModel.new_empty(db)
        query_model.set_sort_order(self.sort_func, None, False)

        if self.query_for_all: # equivalent to use an OR (one query for each parameter)
            log.info('Query for all parameters separatedly')
            for parameter in self.filters:
                query = GLib.PtrArray()
                for static_filter in self.static_filters:
                    db.query_append_params(query, static_filter[0], static_filter[1], static_filter[2])
                db.query_append_params(query, parameter[0], parameter[1], parameter[2])
                db.do_full_query_parsed(query_model, query)
        else:
            log.info('Query for all parameters in one only full search')
            query = GLib.PtrArray()
            for static_filter in self.static_filters:
                db.query_append_params(query, static_filter[0], static_filter[1], static_filter[2]) # Append parameter
            for parameter in self.filters:
                db.query_append_params(query, parameter[0], parameter[1], parameter[2])
            db.do_full_query_parsed(query_model, query)
        return query_model



class InvalidQueryException(Exception):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class RBEntry(object):

    def __init__(self, entry):
        self.id = entry.get_ulong(RB.RhythmDBPropType.ENTRY_ID)
        self.title = entry.get_string(RB.RhythmDBPropType.TITLE) # self.get_value(entry, RB.RhythmDBPropType.TITLE)
        self.artist = entry.get_string(RB.RhythmDBPropType.ARTIST) # self.get_value(entry, RB.RhythmDBPropType.ARTIST)
        self.album = entry.get_string(RB.RhythmDBPropType.ALBUM)
        self.track_number = entry.get_ulong(RB.RhythmDBPropType.TRACK_NUMBER)
        self.duration = entry.get_ulong(RB.RhythmDBPropType.DURATION)
        self.rating = entry.get_double(RB.RhythmDBPropType.RATING)
        self.year = entry.get_ulong(RB.RhythmDBPropType.YEAR)
        self.genre = entry.get_string(RB.RhythmDBPropType.GENRE)
        self.play_count = entry.get_ulong(RB.RhythmDBPropType.PLAY_COUNT)
        self.location = entry.get_string(RB.RhythmDBPropType.LOCATION)
        self.bitrate = entry.get_ulong(RB.RhythmDBPropType.BITRATE)
        self.last_played = entry.get_ulong(RB.RhythmDBPropType.LAST_PLAYED)


class RBSource(object):
    def __init__(self, index, entry, source_type='playlist'):
        self.id = index
        self.index = index
        self.source_type = source_type
        self.is_playing = False # entry[RB_SOURCELIST_MODEL_COLUMN_PLAYING] (Check agains shell.get_playing_source)
        self.name = entry.props.name # entry[RB_SOURCELIST_MODEL_COLUMN_NAME]
        self.source = entry
        self.query_model = entry.props.query_model
        self.entries = None
        self.attributes = None # entry[RB_SOURCELIST_MODEL_COLUMN_ATTRIBUTES]
        self.visibility = None # entry[RB_SOURCELIST_MODEL_COLUMN_VISIBILITY]
        self.is_group = False # entry[RB_SOURCELIST_MODEL_COLUMN_IS_GROUP]
        self.group_category = None #entry[RB_SOURCELIST_MODEL_COLUMN_GROUP_CATEGORY]

