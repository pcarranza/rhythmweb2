
import rb, os, sys

import rbhandle
from rbhandle import RBHandler

from serve import CGIServer
from serve.request import RequestHandler
from serve.conf import Configuration
from serve.log.loggable import Loggable

import serve.log
import logging

class RhythmWeb(rb.Plugin, Loggable):
    
    config = None
    
    def __init__(self):
        base_path = os.path.dirname(__file__)
        
        config_path = os.path.join(base_path, 'cfg', 'rb-serve.conf')
        config = Configuration()
        config.load_configuration(config_path)
        
        serve.log.get_factory().configure(config)
        
        self.base_path = base_path
        self.config = config
        
            
    def activate(self, shell):
        config = self.config
        if config.getBoolean('debug'):
            config.printConfiguration(self)

        request_handler = RequestHandler(self.base_path)
        rbhandler = RBHandler(shell)
        
        server = CGIServer(request_handler, config=config, RB=rbhandler)
        server.start()
        self.server = server
        
        
    def deactivate(self, shell):
        if not self.server is None:
            self.server.stop()


