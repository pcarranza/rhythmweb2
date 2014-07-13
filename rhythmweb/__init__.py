from gi.repository import GObject, Peas
from rbhandle import RBHandler

from rhythmweb.conf import Configuration
from rhythmweb import view, controller
from rhythmweb.server import Server

from serve import CGIServer

import os
import logging
log = logging.getLogger(__name__)


class RhythmWeb(GObject.Object, Peas.Activatable):

    __gtype_name__ = 'RhythmWeb'
    object = GObject.property(type=GObject.GObject)

    def __init__(self):
        GObject.Object.__init__(self)
        config = Configuration()
        logging.basicConfig(filename=config.get_string('log.file'),
                            level=config.get_string('log.level'),
                            format=config.get_string('log.format'))
        self.config = config
        log.info('RhythmWeb plugin created')

    def do_activate(self):
        shell = self.object
        config = self.config
        config.print_configuration()
        controller.set_shell(shell)

        application = Server()
        application.config = config
        server = CGIServer(application)

        server.start()
        shell.server = server
        log.info('RhythmWeb server started')

    def do_deactivate(self):
        shell = self.object
        if shell.server:
            shell.server.stop()
            log.info('RhythmWeb server stopped')
