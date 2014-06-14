from gi.repository import GObject, Peas
from rbhandle import RBHandler

from rhythmweb.conf import Configuration
from rhythmweb import controller

from serve import CGIServer
from serve.app import CGIApplication

import os
import logging
log = logging.getLogger(__name__)


class RhythmWeb(GObject.Object, Peas.Activatable):

    __gtype_name__ = 'RhythmWeb'
    object = GObject.property(type=GObject.GObject)

    def __init__(self):
        GObject.Object.__init__(self)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        config = Configuration()
        logging.basicConfig(filename=config.get_string('log.file'),
                            level=config.get_string('log.level'),
                            format=config.get_string('log.format'))

        self.base_path = base_path
        self.config = config
        log.info('RhythmWeb plugin created')

    def do_activate(self):
        shell = self.object
        config = self.config
        config.print_configuration()
        controller.set_shell(shell)

        application = CGIApplication(self.base_path, config)
        server = CGIServer(application)

        server.start()
        shell.server = server
        log.info('RhythmWeb server started')

    def do_deactivate(self):
        shell = self.object
        if shell.server:
            shell.server.stop()
            log.info('RhythmWeb server stopped')

