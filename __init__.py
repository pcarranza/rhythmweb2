
import rb, os, sys

from serve.conf.config import Configuration
from rbhandle import RBHandler
from serve import CGIServer
from serve.request import RequestHandler
from serve.log.loggable import Loggable


class RhythmWeb(rb.Plugin, Loggable):
    
    _server = None
    _handler = None
    _base_path = None
    
    @staticmethod
    def handler_instance():
        if RhythmWeb._handler is None:
            raise Exception('No instance for RBHandler, not properly setted up')
        
        return RhythmWeb._handler
    
    
    def activate(self, shell):
        RhythmWeb._base_path = os.path.dirname(__file__)
        
        config = Configuration.instance()
        config._params={'port' : '8000', \
                        'log.file' : '/home/jim/rb-serve.log', \
                        'bind' : '0.0.0.0', \
                        'debug' : True }
        
        if Configuration.instance().getBoolean('debug'):
            Configuration.instance().printConfiguration()
        
        self.debug('Base Path: %s' % RhythmWeb._base_path)

        RhythmWeb._handler = RBHandler(shell)
        
        resource_path = os.path.join(RhythmWeb._base_path, 'resources')
        request_handler = RequestHandler(resource_path)
        
        if RhythmWeb._server is None:
            RhythmWeb._server = CGIServer('localhost', 8000, request_handler)
            
        RhythmWeb._server.start()
        
        
    
    
    def deactivate(self, shell):
        if not RhythmWeb._server is None:
            RhythmWeb._server.stop()


