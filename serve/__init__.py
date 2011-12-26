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


from gi.repository import GObject
from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import make_server
from serve.log.loggable import Loggable

from serve.proxy import BufferProxyServer


class CGIServer(Loggable):
    
    __application = None
    __config = None
    __running = False

    __internal_server = None
    __proxy_server = None
    
    def __init__(self, application, config):
        
        if config is None:
            raise Exception('Required component \'config\' not found in components')
        
        self.__config = config
        self.__application = application
        
    
    def start(self):
        self.info('   STARTING SERVER')

        config = self.__config
        
        handle_request = self.__application.handle_request
                
        hostname = config.get_string('hostname', False, 'localhost')
        
        port = config.get_int('port', False, 7001)
        self.info('   HOSTNAME   %s' % hostname)
        self.info('   PORT       %d' % port)

        use_proxy = config.get_boolean('proxy', False, True)
        proxy_port = config.get_int('proxy.port', False, 7000)
        proxy_hostname = config.get_string('proxy.hostname', False, 'localhost')
        
        if self.__internal_server is None:
            self.__internal_server = make_server(
                              hostname, 
                              port, 
                              handle_request,
                              handler_class=LoggingWSGIRequestHandler)
            
        self.__watch_request_loop_id = GObject.io_add_watch(self.__internal_server.socket,
                                                 GObject.IO_IN,
                                                 self.__idle_request_loop)
        
        self.__running = True
        self.info('   SERVER STARTED')
        
        if use_proxy == True:
            self.info('   PROXY_HOSTNAME %s' % proxy_hostname)
            self.info('   PROXY_PORT     %d' % proxy_port)
            
            self.info('   STARTING PROXY')
            self.__proxy_server = BufferProxyServer(proxy_hostname, proxy_port, hostname, port)
            self.__proxy_server.start()
            
            self.info('   PROXY STARTED')
        
        

    def stop(self):
        self.info('   STOPPING SERVER')
        GObject.source_remove(self.__watch_request_loop_id)
        if self.__internal_server is None:
            return
        
        if not self.__proxy_server is None:
            self.info('   STOPPING PROXY SERVER')
            self.__proxy_server.stop()
        
        self.__internal_server = None
        self.__proxy_server = None
        self.__running = False
        self.info('   SERVER STOPPED')
    
    
    def __idle_request_loop(self, source, cb_condition):
        self.debug('Handling request')
        if not self.__running:
            self.debug('NOT RUNNING')
            return False
        self.__internal_server.handle_request()
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
        return 'Request'
    




