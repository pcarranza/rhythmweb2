
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
        self.debug('SHELL object %s' % self._shell)
        self.debug('DB object %s' % self._db)
        self.debug('PLAYER object %s' % self._player)
        self.debug('GCONF object %s' % self._gconf)
        
        
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
    
        
    def get_playing_entry_id(self):
        self.__print_state('get_playing_entry_id')
        entry = self._player.get_playing_entry()
        if entry is None:
            return None
        
        return self._db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
    
        
    def play_entry(self, entry_id): # entry id
        self.__print_state('play_entry')
        self.debug('Playing entry %s' % entry_id)
        self._player.play_entry(entry_id)
    
        
    def set_rating(self, entry, rating):
        self.__print_state('set_rating')
        self.debug('Setting rating %d to entry %s' % (rating, entry))
        self._db.set(entry, rhythmdb.PROP_RATING, rating)
    
        
    def search_song(self, filter):
        self.__print_state('search_song')
        self.debug('Searching for a song with filter %s' % filter)
        return self.search(filter, TYPE_SONG)
    
    
    def search_radio(self, filter):
        self.__print_state('search_radio')
        self.debug('Searching for a radio with filter %s' % filter)
        return self.search(filter, TYPE_RADIO)
    
    
    def search_podcast(self, filter):
        self.__print_state('search_podcast')
        self.debug('Searching for a podcast with filter %s' % filter)
        return self.search(filter, TYPE_PODCAST)
    
    
    def search(self, filter, type):
        self.__print_state('search')
        mtype = self._media_types[type]
        
        db = self._db
        
        searchType = (rhythmdb.QUERY_PROP_EQUALS, \
            rhythmdb.PROP_TYPE, \
            mtype)
        
        searchArtist = (rhythmdb.QUERY_PROP_LIKE, \
            rhythmdb.PROP_ARTIST, \
            filter)
        
        searchAlbum = (rhythmdb.QUERY_PROP_LIKE, \
            rhythmdb.PROP_ALBUM, \
            filter)
        
        searchTitle = (rhythmdb.QUERY_PROP_LIKE, \
            rhythmdb.PROP_TITLE, \
            filter)
        
        query_model = db.query_model_new(db.query_new(), \
                                         rhythmdb.rhythmdb_query_model_track_sort_func, \
                                         0, \
                                         db.query_model_new_empty())
        searchs = (searchArtist, searchAlbum, searchTitle)
        for search in searchs:
            query = db.query_new()
            db.query_append(query, searchType)
            db.query_append(query, search)
            db.do_full_query_parsed(query_model, query)
        
        entries = []
        self._loop_query_model(func=entries.append, query_model=query_model)
        return entries
    
    
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
        self.debug('Getting play queue')
        entries = []
        self._loop_query_model(limit=queue_limit, func=entries.append)
        return entries
    
    
    def enqueue(self, entry_ids):
        self.__print_state('enqueue')
        self.debug('Adding entries %s to queue' % entry_ids)
        for entry_id in entry_ids:
            entry = self.load_entry(entry_id)
            location = str(entry.location)
            self.debug('Enqueuing entry %s' % location)
            self._shell.add_to_queue(location)
                
        self._shell.props.queue_source.queue_draw()
        
    
    def clear_play_queue(self):
        self.__print_state('clear_play_queue')
        self._loop_query_model(func=self._shell.remove_from_queue)


    def load_entry(self, entry_id):
        self.__print_state('load_entry')
        self.debug('Loading entry %s' % str(entry_id))
        entry = self._db.entry_lookup_by_id(int(entry_id))
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
        
    
    def _loop_query_model(self, func, limit=0, query_model=None):
        
        if query_model is None:
            query_model = self._get_play_queue_model()
        
        if query_model.get_size() == 0:
            return
        
        index = 0
        for row in query_model:
            entry = self._get_entry_id(row)
            func(entry)
            
            index = index + 1
            if limit != 0 and index >= limit:
                break
            
    
    def _get_play_queue_model(self):
        return self._shell.props.queue_source.props.query_model
    
    
    def _get_entry_id(self, row):
        entry = row[0]
        return self._db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)

        
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
        