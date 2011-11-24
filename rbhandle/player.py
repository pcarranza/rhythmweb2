

from serve.log.loggable import Loggable


class PlayerHandler(Loggable):
    
    def __init__(self, shell):
        self.__player = shell.get_player()
    
    
    def get_playing_status(self):
        '''
        Gets the playing status, returns True or False according to playing or not
        '''
        self.debug('get playing status')
        return self.__player.get_playing()[1]
    
    
    def get_mute(self):
        '''
        Gets True if the player is muted
        '''
        self.debug('get mute status')
        return self.__player.get_mute()[1]
    
    
    def toggle_mute(self):
        self.debug('toggle mute')
        self.__player.toggle_mute()
        
        
    def get_volume(self):
        '''
        Gets the player volume, a float between 0 and 1
        '''
        self.debug('get volume')
        return self.__player.get_volume()[1]
    
        
    def set_volume(self, volume):
        '''
        Sets the player volume, gets a float between 0 and 1
        '''
        if not type(volume) is float:
            raise Exception('Volume must be a float')
        
        self.debug('set volume %d', volume)
        
        if volume > 1:
            self.warning('Volume cannot be set over 1')
            
        self.__player.set_volume(volume)
    
    
    def get_playing_entry(self):
        '''
        Returns the rhythmbox current playing entry object
        '''
        self.debug('get playing entry')
        return self.__player.get_playing_entry()
    
    
    def get_playing_time(self):
        '''
        Gets the playing time, in seconds
        '''
        self.debug('get playing time')
        return self.__player.get_playing_time()[1]
    
    
    def get_playing_time_string(self):
        '''
        Gets the playing time, as a string in "x:xx of x:xx left" format
        '''
        self.debug('get playing time string')
        return self.__player.get_playing_time_string()
    
    
    def next(self):
        '''
        If playing, skips the player to the next song
        '''
        self.debug('skip to next')
        if self.get_playing_status():
            self.__player.do_next()
        
        
    def seek(self, seconds):
        '''
        Seeks n seconds in the current playing song, receives and int, positive or negative
        '''
        self.debug('seek %d seconds' % seconds)
        self.__player.seek(seconds)
        
        
    def previous(self):
        '''
        If playing, skips the player to the previous song
        '''
        self.debug('skip to previous')
        if self.get_playing_status():
            self.__player.do_previous()
    
    
    def play_pause(self):
        '''
        Starts playing or pauses
        '''
        self.debug('toggle playing status')
        
        status = self.get_playing_status()
        return self.__player.playpause(not status)
    
    
    def __play_entry(self, entry):
        '''
        Inmediately starts playing provided entry
        '''
        self.debug('play entry')
        if not entry is None:
            if self.get_playing_status():
                self.play_pause()
            
            self.__player.play_entry(entry)

