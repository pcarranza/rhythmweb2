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
import sys
import traceback

import serve.log

from io import StringIO
from gi.repository import GObject, Peas
from rbhandle import RBHandler

from serve import CGIServer
from serve.log.loggable import Loggable

from rhythmweb.conf import Configuration

from serve.app import CGIApplication

class RhythmWeb(GObject.Object, Peas.Activatable, Loggable):

    __gtype_name__ = 'RhythmWeb'
    object = GObject.property(type=GObject.GObject)


    def __init__(self):
        GObject.Object.__init__(self)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        config = Configuration()
        serve.log.get_factory().configure(config)

        self.base_path = base_path
        self.config = config

        resource_path = os.path.join(base_path, 'resources')
        self.info('RhythmWeb loaded')


    def do_activate(self):
        shell = self.object
        config = self.config

        config.print_configuration()
        rbhandler = RBHandler(shell)

        components = {'config' : config, 'RB' : rbhandler}

        application = CGIApplication('RhythmWeb', self.base_path, components)

        server = CGIServer(application, config)
        server.start()
        shell.server = server



    def do_deactivate(self):
        shell = self.object
        if not shell.server is None:
            shell.server.stop()

        del shell.server
        del self.config
        del self.base_path

