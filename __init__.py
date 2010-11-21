
import rb, os

from serve.server import HttpServer
from serve.conf.config import Configuration

class RhythmWeb(rb.Plugin):
    
    ns = None
    
    def activate(self, shell):
        config = Configuration.instance()
        config._params={'port' : '8000', \
                        'log.file' : '/home/jim/rb-serve.log', \
                        'bind' : '0.0.0.0' }
        if Configuration.instance().getBoolean('debug'):
            Configuration.instance().printConfiguration()
        self.ns = HttpServer()
        self.ns.start()
        print 'activated'
    
    
    def deactivate(self, shell):
        self.ns.stop()
        
        print 'deactivated'
