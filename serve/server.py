
from serve.conf.config import Configuration
from serve.log.loggable import Loggable
import BaseHTTPServer
import os
import threading


class HttpServer(Loggable, threading.Thread):
    ''' Runs the http server, mainly  '''
    _HTTPServer = None
    _port = 8000
    
    def __init__(self):
        ''' Creates the server object using loaded configuration.
            Mainly it uses 2 configurations parameters: "bind" (127.0.0.1 by default) and "port" 
        '''
        bind_address = Configuration.instance().getString('bind', False, '127.0.0.1')
        port = Configuration.instance().getInt('port', False, 8000)
        self._port = port
        
        self.info('Starting server in port %d binded to address %s' % (port, bind_address))
        
        server_address = (bind_address, port)
        
        self._HTTPServer = BaseHTTPServer.HTTPServer(server_address, RBRequest)
        threading.Thread.__init__(self, target=self.run)
    
    
    def run(self):
        self.info('Server up and running in port %d' % self._port)
        self._HTTPServer.serve_forever()
        
        
    def stop(self):
        self.info('Stopping server in port %d' % self._port)
        self._HTTPServer.shutdown()
        self._HTTPServer.socket.close()
    
    
class RBRequest(BaseHTTPServer.BaseHTTPRequestHandler, Loggable):

    _resources = {}
    _path_pattern = 'web.%s'
    
    def check_path(self, path):
        p = os.path.basename(path)
        if not p:
            return 'home'
        
        filename = os.path.splitext(p)[0]
        extension = os.path.splitext(p)[1]
        if not extension:
            return filename
        
        return 'res:%s' % path
        
    
    def do_GET(self):
        path = self.check_path(self.path)
        self.info('GET Method: %s' % path)
        if path.startswith(ResourceHandler._prefix):
            resource = self.get_resource_handler(path)
            if not resource.exists():
                self.error(code=404, message='resource not found')
                return
            
            resource.handle(self)
            return
        
        path = str(path).replace('/', '.')
        page_path = self._path_pattern % path
        mod = __import__(page_path, globals(), locals(), ['Page'])
        
        if not mod:
            self.error(code=404, message='Could not find page %s' % page_path)
            return
            
        klass = getattr(mod, 'Page')
        if not klass:
            self.error(code=500, message='Page file %s does not contains a Page class' % page_path)
            return
        
        instance = klass(self)
        if not instance:
            self.error(code=500, message='Could not create instace for page %s' % page_path)
            return
        
        try:
            instance.render_page()
        except Exception as e:
            self.error(code=500, message=e.message)
    
    
    def do_POST(self):
        self.error(500, "POST not implemented")
    
    
    def do_PUT(self):
        self.error(500, "PUT not implemented")
    
    
    def do_DELETE(self):
        self.error(500, "DELETE not implemented")
    
    
    def error(self, code=500, message=None):
        self.send_error(code, message);
        
    
    def get_resource_handler(self, res):
        if not self._resources.has_key(res):
            self._resources[res] = ResourceHandler(res)
            
        return self._resources[res]
        

class ResourceHandler:
    
    _prefix = 'res:'
    _content_type = None
    _open_as = None
    _file = None
    _extension = None
    _exists = False
    
    def __init__(self, res, content_type=None, open_as=''):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, 'resources')
        
        resource = str(res).replace(ResourceHandler._prefix, '')
        resource = os.path.basename(resource)
        
        self._content_type = content_type
        self._open_as = open_as
        
        self._file = os.path.join(cwd, resource)
        self._extension = str(os.path.splitext(self._file)[1]).lower()
        self._exists = os.path.exists(self._file)
        
        
    def exists(self):
        return self._exists
    
    
    def handle(self, request):
        (content_type, open_as) = self._get_content_type()
        if not content_type:
            raise UnknownContentTypeException(self._extension)
        
        request.send_response(200)
        request.send_header("Content-type", content_type)
        request.end_headers()

        open_mode = 'r%s' % open_as
        
        file = open(self._file, open_mode)
        
        try:
            while True:
                line = file.next()
                request.wfile.write(line)
        except StopIteration:
            file.close()
        

    def _get_content_type(self):
        if not self._content_type:
            (self._content_type, self._open_as) = self._content_type_by_ext(self._extension)
        
        return (self._content_type, self._open_as)
    
    
    def _content_type_by_ext(self, ext):
        if ext == '.css':
            return ('text/css', 't')
        if ext == '.gif':
            return ('image/gif', 'b')
        if ext == '.png':
            return ('image/x-png', 'b')
        if ext == '.jpg':
            return ('image/jpeg', 'b')
        if ext == '.jpeg':
            return ('image/jpeg', 'b')
        if ext == '.ico':
            return ('image/ico', 'b')
        
        return ('text/plain', 't')
    
    
class UnknownContentTypeException(Exception):
    
    def __init__(self, ext):
        Exception.__init__(self)
        self.message = 'Unknown content type %s' % ext
