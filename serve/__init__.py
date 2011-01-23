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

import sys
import gobject
import cgi

from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import make_server
from serve.log.loggable import Loggable



class CGIServer(Loggable):
    
    __hostname = None
    __port = None
    __httpd = None
    __application = None
    __config = None
    __running = False
    
    def __init__(self, application, config):
        
        if config is None:
            raise Exception('Required component \'config\' not found in components')
        
        self.__config = config
        self.__application = application
        self.__hostname = config.getString('hostname', False, 'localhost')
        self.__port = config.getInt('port', False, 7000)
        
    
    def start(self):
        self.info('   STARTING SERVER')
        self.info('   HOSTNAME   %s' % self.__hostname)
        self.info('   PORT       %d' % self.__port)

        if self.__httpd is None:
            self.__httpd = make_server(self.__hostname, 
                              self.__port, 
                              self.__application.handle_request,
                              handler_class=LoggingWSGIRequestHandler)
        self._watch_cb_id = gobject.io_add_watch(self.__httpd.socket,
                                                 gobject.IO_IN,
                                                 self.__idle_cb)
        self.__running = True
        self.info('   SERVER STARTED')
        

    def stop(self):
        self.info('   STOPPING SERVER')
        gobject.source_remove(self._watch_cb_id)
        if self.__httpd is None:
            return
        
        self.__httpd = None
        self.__running = False
        self.info('   SERVER STOPPED')
    
    
    def __idle_cb(self, source, cb_condition):
        if not self.__running:
            return False
        self.__httpd.handle_request()
        return True
    
    
    
    
    
class LoggingWSGIRequestHandler(WSGIRequestHandler, Loggable):
    '''
    Request handler, ends up invoking app method
    '''
    
    def get_environ(self):
        '''
        Just in case I need to add something...
        '''
        return WSGIRequestHandler.get_environ(self)
    
    
    def log_message(self, format, *args):
        self.info('%s - [%s] %s' %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))
    
    def get_logname(self):
        return 'REQUEST'