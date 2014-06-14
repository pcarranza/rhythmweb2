import logging
log = logging.getLogger(__name__)


ORDER_LINEAR = 'linear'
ORDER_SHUFFLE = 'shuffle'
ORDER_SHUFFLE_BY_AGE_AND_RATING = 'random-by-age-and-rating'
ORDER_SHUFFLE_BY_AGE = 'random-by-age'
ORDER_SHUFFLE_BY_RATING = 'random-by-rating'
ORDER_SHUFFLE_EQUALS = 'random-equal-weights'

PLAY_ORDER_KEY = '/apps/rhythmbox/state/play_order'
PLAY_LOOP = '-loop'

class PlayerHandler(object):
    
    def __init__(self, shell):
        self.shell = shell
        self.player = shell.props.shell_player
        
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
        
#        self.__gconf = gconf.client_get_default()
#        self.__playing_song = None
#        self.player.connect('playing-song-changed', self.__playing_song_changed)
    
    
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
    
    
#    def __playing_song_changed(self, player, entry):
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

