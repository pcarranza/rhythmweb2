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
    __request_handler = None
    __running = False
    
    __components = None
    
    def __init__(self, request_handler, **components):
        
        config = None
        
        if components:
            self.__components = {}
        
        for component in components:
            if component == 'config':
                config = components[component]
            
            self.__components[component] = components[component]
            
        if config is None:
            raise Exception('Required component \'config\' not found in components')
        
        self.__request_handler = request_handler
        self.__hostname = config.getString('hostname', False, 'localhost')
        self.__port = config.getInt('port', False, 7000)
        
    
    def start(self):
        self.debug('STARTING SERVER')
        self.debug('HOSTNAME   %s' % self.__hostname)
        self.debug('PORT       %d' % self.__port)

        if self.__httpd is None:
            self.__httpd = make_server(self.__hostname, 
                              self.__port, 
                              self.__handle,
                              handler_class=LoggingWSGIRequestHandler)
        self._watch_cb_id = gobject.io_add_watch(self.__httpd.socket,
                                                 gobject.IO_IN,
                                                 self.__idle_cb)
        self.__running = True
        self.debug('SERVER STARTED')
        

    def stop(self):
        self.debug('STOPPING SERVER')
        gobject.source_remove(self._watch_cb_id)
        if self.__httpd is None:
            return
        
        self.__httpd = None
        self.__running = False
        self.debug('SERVER STOPPED')
    
    
    def __idle_cb(self, source, cb_condition):
        if not self.__running:
            return False
        self.__httpd.handle_request()
        return True
    
    
    def __handle(self, environ, response):
        
        method = environ['REQUEST_METHOD']
        
        for component in self.__components:
            self.debug('%s = %s' % (component, self.__components[component]))
        
        self.debug('Handling method %s' % method)
        try:
            if method == 'GET':
                return self.__do_get(environ, response)
            
            elif method == 'POST':
                params = self.parse_post(environ)
                
                if params is None:
                    self.debug('No parameters in POST method')
                    
                for p in params:
                    self.debug('POST %s = %s' % (p, str(params[p])))
                    
                return self.__do_post(environ, params, response)
            
            return self.__request_handler.send_error(
                 500, 
                 '%s Not implemented' % method, 
                 response)
            
        except Exception, e:
            return self.__request_handler.send_error(
                 500, 
                 '%s Unknown exception' % e, 
                 response)
            
            
    def __do_get(self, environ, response):
        return self.__request_handler.do_get(environ, response, self.__components)
        
        
    def __do_post(self, environ, params, response):
        return self.__request_handler.do_post(environ, params, response, self.__components)
            
            
    def parse_post(self, environ):
        self.debug('Parsing post parameters')
        
        if 'CONTENT_TYPE' in environ:
            length = -1
            if 'CONTENT_LENGTH' in environ:
                length = int(environ['CONTENT_LENGTH'])
                
            if environ['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
                return cgi.parse_qs(environ['wsgi.input'].read(length))
            
            if environ['CONTENT_TYPE'] == 'multipart/form-data':
                return cgi.parse_multipart(environ['wsgi.input'].read(length))
            
            else:
                return cgi.parse_qs(environ['wsgi.input'].read(length))
            
        return None
    
    
    
class LoggingWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, format, *args):
        sys.stdout.write("%s - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))