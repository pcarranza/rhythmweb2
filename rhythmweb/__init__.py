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
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os
import logging

import serve.log

from gi.repository import GObject, Peas
from rbhandle import RBHandler

from serve import CGIServer

from rhythmweb.conf import Configuration

from serve.app import CGIApplication


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
        self.log = logging.getLogger(__name__)

        self.base_path = base_path
        self.config = config

        self.log.info('RhythmWeb plugin created')

    def do_activate(self):
        shell = self.object
        config = self.config

        config.print_configuration()
        rbhandler = RBHandler(shell)

        components = {'config': config, 'RB': rbhandler}

        application = CGIApplication('RhythmWeb', self.base_path, components)

        server = CGIServer(application, config)
        server.start()
        shell.server = server
        self.log.info('RhythmWeb server started')

    def do_deactivate(self):
        shell = self.object
        if shell.server:
            shell.server.stop()
            self.log.info('RhythmWeb server stopped')