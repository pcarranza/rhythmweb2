
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
    
    def __init__(self, hostname, port, request_handler):
        self._hostname = hostname
        self._port = port
        self._request_handler = request_handler
    
    
    def start(self):
        if self._httpd is None:
            self._httpd = make_server(self._hostname, 
                              self._port, 
                              self._handle,
                              handler_class=LoggingWSGIRequestHandler)
        self._watch_cb_id = gobject.io_add_watch(self._httpd.socket,
                                                 gobject.IO_IN,
                                                 self._idle_cb)
        self._running = True

    def stop(self):
        gobject.source_remove(self._watch_cb_id)
        if self._httpd is None:
            return
        
        self._httpd = None
        self._running = False
    
    
    def _idle_cb(self, source, cb_condition):
        if not self._running:
            return False
        self._httpd.handle_request()
        return True
    
    
    def _handle(self, environ, response):
        
        method = environ['REQUEST_METHOD']
        
        self.debug('Handling method %s' % method)
        
        if method == 'GET':
            return self._do_get(environ, response)
        
        elif method == 'POST':
            params = self.parse_post(environ)
            
            if params is None:
                self.debug('No parameters in POST method')
                
            for p in params:
                self.debug('POST %s = %s' % (p, str(params[p])))
                
            #if 'action' in params:
            return self._do_post(environ, params, response)
        
        return self._request_handler.send_error(
             500, 
             '%s Not implemented' % method, 
             response)
            
            
    def _do_get(self, environ, response):
        return self._request_handler.do_get(environ, response)
        
        
    def _do_post(self, environ, params, response):
        return self._request_handler.do_post(environ, params, response)
            
            
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