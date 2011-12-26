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
import serve.log

from gi.repository import GObject, Peas
from rbhandle import RBHandler

from serve import CGIServer
from serve.conf import Configuration
from serve.log.loggable import Loggable

from serve.app import CGIApplication

class RhythmWeb(GObject.Object, Peas.Activatable, Loggable):
    
    __gtype_name__ = 'RhythmWeb'
#    object = GObject.property(type=GObject.GObject)
    
    
    def __init__(self):
        GObject.Object.__init__(self)
        base_path = os.path.dirname(__file__)
        
        config_path = os.path.join(base_path, 'cfg', 'rb-serve.conf')
        
        config = Configuration()
        config.load_configuration(config_path)
        serve.log.get_factory().configure(config)
        
        self.base_path = base_path
        self.config = config
        self.config_path = config_path
        
        resource_path = os.path.join(base_path, 'resources')
        config.put('*resources', resource_path)
        self.info('RhythmWeb loaded')

    
    def do_activate(self):
        shell = self.object
        config = self.config

        config.print_configuration(self)
        rbhandler = RBHandler(shell)
        
        components = {'config' : config, 'RB' : rbhandler}
        
        application = CGIApplication('RhythmWeb', self.base_path, components)
        
        server = CGIServer(application, config)
        server.start()
        shell.server = server
        
#        self.preferences = Preferences(config, self.config_path)
        
        
    def do_deactivate(self):
        shell = self.object
        if not shell.server is None:
            shell.server.stop()
        
        del shell.server
        del self.config
        del self.config_path
        del self.base_path

#        if not self.preferences.button == None:
#            self.preferences.button.disconnect(self.connect_id_pref2)
#        del self.preferences 


#    def create_configure_dialog(self, dialog=None):
#        dialog = self.preferences.show_dialog()
#        self.connect_id_pref2 = self.preferences.button.connect('clicked', lambda x: dialog.destroy() )
#        return dialog

