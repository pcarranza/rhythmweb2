from gi.repository import RB

import logging
log = logging.getLogger(__name__)


class EntryHandler(object):
    
    def __init__(self, shell):
        self.db = shell.props.db
        
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

