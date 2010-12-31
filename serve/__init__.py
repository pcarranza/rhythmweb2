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
    
    _hostname = None
    _port = None
    _httpd = None
    _request_handler = None
    _running = False
    
    _components = None
    
    def __init__(self, request_handler, **components):
        
        config = None
        
        if components:
            self._components = {}
        
        for component in components:
            if component == 'config':
                config = components[component]
            
            self._components[component] = components[component]
            
        if config is None:
            raise Exception('Required component \'config\' not found in components')
        
        self._request_handler = request_handler
        self._hostname = config.getString('hostname', False, 'localhost')
        self._port = config.getInt('port', False, 8000)
        
    
    def start(self):
        self.debug('STARTING SERVER')
        self.debug('HOSTNAME   %s' % self._hostname)
        self.debug('PORT       %d' % self._port)

        if self._httpd is None:
            self._httpd = make_server(self._hostname, 
                              self._port, 
                              self._handle,
                              handler_class=LoggingWSGIRequestHandler)
        self._watch_cb_id = gobject.io_add_watch(self._httpd.socket,
                                                 gobject.IO_IN,
                                                 self._idle_cb)
        self._running = True
        self.debug('SERVER STARTED')
        

    def stop(self):
        self.debug('STOPPING SERVER')
        gobject.source_remove(self._watch_cb_id)
        if self._httpd is None:
            return
        
        self._httpd = None
        self._running = False
        self.debug('SERVER STOPPED')
    
    
    def _idle_cb(self, source, cb_condition):
        if not self._running:
            return False
        self._httpd.handle_request()
        return True
    
    
    def _handle(self, environ, response):
        
        method = environ['REQUEST_METHOD']
        
        for component in self._components:
            self.debug('%s = %s' % (component, self._components[component]))
        
        self.debug('Handling method %s' % method)
        
        if method == 'GET':
            return self._do_get(environ, response)
        
        elif method == 'POST':
            params = self.parse_post(environ)
            
            if params is None:
                self.debug('No parameters in POST method')
                
            for p in params:
                self.debug('POST %s = %s' % (p, str(params[p])))
                
            return self._do_post(environ, params, response)
        
        return self._request_handler.send_error(
             500, 
             '%s Not implemented' % method, 
             response)
            
            
    def _do_get(self, environ, response):
        return self._request_handler.do_get(environ, response, self._components)
        
        
    def _do_post(self, environ, params, response):
        return self._request_handler.do_post(environ, params, response, self._components)
            
            
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
        # RB redirects stdout to its logging system, to these
        # request log messages, run RB with -D rhythmweb
        sys.stdout.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))