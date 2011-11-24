
from serve.log.loggable import Loggable
from gi.repository import RB, GObject


class EntryHandler(Loggable):
    
    def __init__(self, shell):
        self.__db = shell.props.db
        
    def get_entry(self, entry_id):
        '''
        Returns an entry by its id
        '''
        if not str(entry_id).isdigit():
            raise Exception('entry_id parameter must be an int')
        
        entry_id = int(entry_id)
        
        self.trace('Getting entry %d' % entry_id)
        return self.__db.entry_lookup_by_id(entry_id)
        
        
    def load_rb_entry(self, entry_id):
        '''
        Returns a RBEntry with the entry information fully loaded for the given id 
        '''
        self.debug('Loading entry %s' % str(entry_id))
        entry = self.get_entry(entry_id)
        if entry is None:
            self.info('Entry %s not found' % str(entry_id))
            return None
        
        rbentry = RBEntry()
        rbentry.id = self.get_value(entry, RB.RhythmDBPropType.ENTRY_ID)
        rbentry.title = self.get_value(entry, RB.RhythmDBPropType.TITLE)
        rbentry.artist = self.get_value(entry, RB.RhythmDBPropType.ARTIST)
        rbentry.album = self.get_value(entry, RB.RhythmDBPropType.ALBUM)
        rbentry.track_number = self.get_value(entry, RB.RhythmDBPropType.TRACK_NUMBER)
        rbentry.duration = self.get_value(entry, RB.RhythmDBPropType.DURATION)
        rbentry.rating = self.get_value(entry, RB.RhythmDBPropType.RATING)
        rbentry.year = self.get_value(entry, RB.RhythmDBPropType.YEAR)
        rbentry.genre = self.get_value(entry, RB.RhythmDBPropType.GENRE)
        rbentry.play_count = self.get_value(entry, RB.RhythmDBPropType.PLAY_COUNT)
        rbentry.location = self.get_value(entry, RB.RhythmDBPropType.LOCATION)
        rbentry.bitrate = self.get_value(entry, RB.RhythmDBPropType.BITRATE)
        rbentry.last_played = self.get_value(entry, RB.RhythmDBPropType.LAST_PLAYED)
        
        return rbentry
    
    
    def set_rating(self, entry_id, rating):
        '''
        Sets the provided rating to the given entry id, int 0 to 5 
        '''
        if not type(rating) is int:
            raise Exception('Rating parameter must be an int')
        
        self.info('Setting rating %d to entry %s' % (rating, entry_id))
        entry = self.get_entry(entry_id)
        if not entry is None:
            self.__db.set(entry, RB.RhythmDBPropType.RATING, rating)

    
    
    def get_entry_id(self, entry):
        return self.get_value(entry, RB.RhythmDBPropType.ENTRY_ID)
    
    
    def get_value(self, entry, property_type):
        self.trace('Loading value %s' % str(property_type))
        
        t = self.__db.get_property_type(property_type)
        value = GObject.Value()
        value.init(t)
        
        self.__db.entry_get(entry, property_type, value)
        
        if t.name == 'gulong':
            return value.get_ulong()
            
        elif t.name == 'gchararray':
            return value.get_string()
            
        elif t.name == 'gboolean':
            return value.get_boolean()
            
        elif t.name == 'gboxed':
            return value.get_boxed()
            
        elif t.name == 'gchar':
            return value.get_char()
            
        elif t.name == 'gdouble':
            return value.get_double()
            
        elif t.name == 'genum':
            return value.get_enum()
            
        elif t.name == 'gflags':
            return value.get_flags()
            
        elif t.name == 'gfloat':
            return value.get_float()
            
        elif t.name == 'gint':
            return value.get_int()
            
        elif t.name == 'gint64':
            return value.get_int64()
            
        elif t.name == 'glong':
            return value.get_long()
            
        elif t.name == 'gobject':
            return value.get_object()
            
        elif t.name == 'gparam':
            return value.get_param()
            
        elif t.name == 'gpointer':
            return value.get_pointer()
            
        elif t.name == 'gstring':
            return value.get_string()
            
        elif t.name == 'guchar':
            return value.get_uchar()
            
        elif t.name == 'guint':
            return value.get_uint()
            
        elif t.name == 'guint64':
            return value.get_uint64()
            
        elif t.name == 'gvariant':
            return value.get_variant()
            
        else:
            self.warning('Unknown type %s' % t.name)
            return None


class RBEntry():
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

