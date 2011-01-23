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
        config.printConfiguration(self)

        request_handler = RequestHandler(self.base_path)
        rbhandler = RBHandler(shell)
        
        server = CGIServer(request_handler, config=config, RB=rbhandler)
        server.start()
        shell.server = server
        
        
        
    def deactivate(self, shell):
        if not shell.server is None:
            shell.server.stop()


