
from serve.page.base import BasePanel

class StatusPanel(BasePanel):
    
    handler = None
    
    def __init__(self, request, handler):
        BasePanel.__init__(self, request, __file__)
        self.handler = handler
        
    def name(self):
        return 'Status'
    
    
    def render_template(self, node):
        handler = self.handler
        bstatus = handler.getStatus()
        
        status = "Paused"
        artist = "[N/A]"
        album = "[N/A]"
        title = "[N/A]"
        time = "[N/A]"

        if bstatus:
            status = "Playing"
            
        try:
            artist = handler.getArtist()
            album = handler.getAlbum()
            title = handler.getTitle()
        except Exception as e:
            self.error(e.message)
        
        try:
            currentTime = handler.timeHumanReadable(handler.getTrackCurrentTime())
            if handler.getTrackTotalTime() == 0:
                time = currentTime
            else:
                totalTime = handler.timeHumanReadable(handler.getTrackTotalTime())
                time = "%s/%s" % (currentTime, totalTime)
                    
        except Exception as e:
            status = "Unknown"
            self.error(e.message)

        node.status.content = status
        node.artist.content = artist
        node.album.content = album
        node.title.content = title
        node.time.content = time
        