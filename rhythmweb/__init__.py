from gi.repository import GObject, Peas

from rhythmweb.rb import RBHandler
from rhythmweb import view, controller
from rhythmweb.server import Server

import os
import logging

log = logging.getLogger(__name__)


class RhythmWeb(GObject.Object, Peas.Activatable):

    __gtype_name__ = 'RhythmWeb'
    object = GObject.property(type=GObject.GObject)

    def __init__(self):
        GObject.Object.__init__(self)
        log.info('RhythmWeb plugin created')

    def do_activate(self):
        shell = self.object
        controller.set_shell(shell)
        server = Server()
        server.start()
        shell.server = server
        log.info('RhythmWeb server started')

    def do_deactivate(self):
        shell = self.object
        if shell.server:
            shell.server.stop()
            log.info('RhythmWeb server stopped')
