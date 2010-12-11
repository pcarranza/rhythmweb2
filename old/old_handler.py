
import dbus, os
from subprocess import Popen, PIPE

class RhythmboxHandler():
    
    player = None
    shell = None
    playlist = None
    volume = 0
    display = None
    
    def __init__(self):
        bus = dbus.SessionBus()
        rbox = bus.get_object( 'org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Player')
        rboxs = bus.get_object( 'org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Shell')
        rboxp = bus.get_object( 'org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/PlaylistManager')
        self.player = dbus.Interface(rbox, 'org.gnome.Rhythmbox.Player')
        self.shell = dbus.Interface(rboxs, 'org.gnome.Rhythmbox.Shell')
        self.playlist = dbus.Interface(rboxp, 'org.gnome.Rhythmbox.PlaylistManager')
        
        self.display = os.environ['DISPLAY']
        if not self.display:
            raise InvalidConfigurationError("No DISPLAY variable set")
        
    
    
    def _getSongProperties(self):
        return self.shell.getSongProperties(self.player.getPlayingUri())
    

    def getCoverImagePath(self):
        try:
            cover = open(self._getSongProperties()['rb:coverArt-uri'] )
            reply = cover.read()
            cover.close()
        except IOError:
            reply=""
        
        return reply
    
    
    def coverExists(self):
        song_properties = self._getSongProperties();
        coverExists = False
        if song_properties.has_key('rb:coverArt-uri'):
            coverExists=True
            artwork_path = song_properties['rb:coverArt-uri'] 
            if os.path.isfile(artwork_path):
                size = int(os.path.getsize(artwork_path))
                if size > 200000:
                    coverExists=False
            else:
                coverExists=False
        return coverExists

    
    def playPause(self):
        self.player.playPause(1)

        
    def next(self):
        self.player.next()


    def prev(self):
        self.player.previous()

    def volDown(self):
        currVol = self.player.getVolume()
        currVol = currVol-0.1
        if currVol < 0:
            currVol=0
        self.player.setVolume(currVol)
       
    
    def volUp(self):
        self.player.setVolume(self.player.getVolume()+0.1)
    
    
    def mute(self):
        if self.player.getMute() == True:
            self.player.setMute(False)
        else:
            self.player.setMute(True)
    
    def getStatus(self):
        if self.player.getPlaying() != 0:
            return True
        return False
    
        
    def getAlbum(self):
        return str(self._getSongProperties()["album"])

    
    def getArtist(self):
        return str(self._getSongProperties()["artist"])

    
    def getTitle(self):
        return str(self._getSongProperties()["title"])
    
    
    def getTrackCurrentTime(self):
        return int(self.player.getElapsed())
    
    
    def getTrackTotalTime(self):
        return int(self._getSongProperties()['duration'])

    
    def seek(self, seconds):
        self.player.setElapsed(int(seconds))


# Not implmented in RB 0.11 dbus interface
#gboolean            rb_shell_player_get_playback_state  (RBShellPlayer *player,
#                                                         gboolean *shuffle,
#                                                         gboolean *repeat);
#    def getShuffle(self):
#        (shuffle, repeat) = self.player.getPlaybackState()
#void                rb_shell_player_set_playback_state  (RBShellPlayer *player,
#                                                         gboolean shuffle,
#                                                         gboolean repeat);
#    def setShuffle(self):
#        pass
#    def setRepeat(self):
#        pass

    def getInfo(self):
        reply = None
        try:
            sep = '/'
            status = self.getStatus()
            album = self.getAlbum()
            artist = self.getArtist()
            title = self.getTitle()
            trackCurrentTime = self.timeHumanReadable(self.getTrackCurrentTime())
            trackTotalTime = self.timeHumanReadable(self.getTrackTotalTime())
            coverExists = str(self.coverExists())
                 
            reply = status + sep + \
                    album + sep + \
                    artist + sep + \
                    title + sep + \
                    trackCurrentTime + sep + \
                    trackTotalTime + sep + \
                    coverExists

        except Exception, e:
            reply = "ERROR - " + e.message
        
        return reply
    
    def timeHumanReadable(self, time):
        minutes = time / 60
        seconds = time % 60
        if minutes > 60:
            hours = minutes / 60
            minutes = minutes % 60
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        
        return "%d:%02d" % (minutes, seconds)
#    client_socket.close()



class InvalidConfigurationError(Exception):
    
    def __init__(self, message):
        Exception.__init__(self, message)
        