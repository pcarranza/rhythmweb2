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


from serve.log.loggable import Loggable
#from gi.repository import RB

ORDER_LINEAR = 'linear'
ORDER_SHUFFLE = 'shuffle'
ORDER_SHUFFLE_BY_AGE_AND_RATING = 'random-by-age-and-rating'
ORDER_SHUFFLE_BY_AGE = 'random-by-age'
ORDER_SHUFFLE_BY_RATING = 'random-by-rating'
ORDER_SHUFFLE_EQUALS = 'random-equal-weights'

PLAY_ORDER_KEY = '/apps/rhythmbox/state/play_order'
PLAY_LOOP = '-loop'

class PlayerHandler(Loggable):
    
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
        self.debug('get playing status')
        return self.player.get_playing()[1]
    
    
    def get_mute(self):
        '''
        Gets True if the player is muted
        '''
        self.debug('get mute status')
        return self.player.get_mute()[1]
    
    
    def toggle_mute(self):
        self.debug('toggle mute')
        self.player.toggle_mute()
        
        
    def get_volume(self):
        '''
        Gets the player volume, a float between 0 and 1
        '''
        self.debug('get volume')
        return self.player.get_volume()[1]
    
        
    def set_volume(self, volume):
        '''
        Sets the player volume, gets a float between 0 and 1
        '''
        if not type(volume) is float:
            raise Exception('Volume must be a float')
        
        self.debug('set volume %d', volume)
        
        if volume > 1:
            self.warning('Volume cannot be set over 1')
            
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
        self.debug('get playing entry')
        return self.player.get_playing_entry()
    
    
    def get_playing_time(self):
        '''
        Gets the playing time, in seconds
        '''
        self.debug('get playing time')
        return self.player.get_playing_time()[1]
    
    
    def get_playing_time_string(self):
        '''
        Gets the playing time, as a string in "x:xx of x:xx left" format
        '''
        self.debug('get playing time string')
        return self.player.get_playing_time_string()
    
    
    def next(self):
        '''
        If playing, skips the player to the next song
        '''
        self.debug('skip to next')
        if self.get_playing_status():
            self.player.do_next()
        
        
    def seek(self, seconds):
        '''
        Seeks n seconds in the current playing song, receives and int, positive or negative
        '''
        self.debug('seek %d seconds' % seconds)
        self.player.seek(seconds)
        
        
    def previous(self):
        '''
        If playing, skips the player to the previous song
        '''
        self.debug('skip to previous')
        if self.get_playing_status():
            self.player.do_previous()
    
    
    def play_pause(self):
        '''
        Starts playing or pauses
        '''
        self.debug('toggle playing status')
        
        status = self.get_playing_status()
        return self.player.playpause(not status)
    
    
    def play_entry(self, entry_id): # entry id
        '''
        Inmediatly starts playing the entry which id gets by parameter
        '''
        self.info('Playing entry %s' % entry_id)
        
        entry = self.get_entry(entry_id)
        if not entry is None:
            self._play_entry(entry)
    
    
    def _play_entry(self, entry):
        '''
        Inmediately starts playing provided entry
        '''
        self.debug('play entry')
        if not entry is None:
            if self.get_playing_status():
                self.play_pause()
            
            self.player.play_entry(entry)
    
    
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
        if self._play_toggle_loop.has_key(order):
            new_order = self._play_toggle_loop[order]
        self.set_play_order(new_order)
    
    
#    def __playing_song_changed(self, player, entry):
#        self.debug('Playing song changed....')
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

