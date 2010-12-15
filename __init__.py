
import rb, os, sys

from serve.conf.config import Configuration
from rbhandle import RBHandler
from serve import CGIServer
from serve.request import RequestHandler
from serve.log.loggable import Loggable
from serve.log.factory import LoggerFactory


class RhythmWeb(rb.Plugin, Loggable):
    
    _server = None
    _handler = None
    _base_path = None
    
    @staticmethod
    def handler_instance():
        if RhythmWeb._handler is None:
            raise Exception('No instance for RBHandler, not properly setted up')
        
        return RhythmWeb._handler
    
    
    def __init__(self):
        base_path = os.path.dirname(__file__)
        
        config_path = os.path.join(base_path, 'rb-serve.conf')
        configuration = Configuration.get_instance()
        configuration.load_configuration(config_path)
        
        LoggerFactory.get_factory().configure(configuration)
        
        RhythmWeb._base_path = base_path
        
    
    def activate(self, shell):
        config = Configuration.get_instance()
        
        if config.getBoolean('debug'):
            config.printConfiguration(self)
        
        self.debug('Base Path: %s' % RhythmWeb._base_path)

        RhythmWeb._handler = RBHandler(shell)
        
        resource_path = os.path.join(RhythmWeb._base_path, 'resources')
        request_handler = RequestHandler(resource_path)
        
        hostname = config.getString('hostname', False, 'localhost')
        port = config.getInt('port', False, 8000)
        
        if RhythmWeb._server is None:
            RhythmWeb._server = CGIServer(hostname, port, request_handler)
            
        RhythmWeb._server.start()
        
        
    
    
    def deactivate(self, shell):
        if not RhythmWeb._server is None:
            RhythmWeb._server.stop()


