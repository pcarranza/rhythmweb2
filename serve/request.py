
import os
from serve.log.loggable import Loggable

class RequestHandler(Loggable):
    
    _resources = {}
    _resource_path = None
    _path_pattern = 'web.%s'
    
    def __init__(self, resource_path):
        self.info('Request Handler started')
        self._resource_path = resource_path
    
    def do_get(self, environ, response):
        self.info('Invoking get method')
        return self.handle_method('get', environ, response)
    
    def do_post(self, environ, params, response):
        self.info('Invoking post method')
        
        
        self.debug('POST parameters:')
        for param in params:
            self.debug("%s = %s" % (param, params[param]))
        
#        self.debug('POST environment:')    
#        for env in environ:
#            self.debug("%s = %s" % (env, environ[env]))

        return self.handle_method('post', environ, response, params)
        
    
    def handle_method(self, request_method, environ, response, params=None):
        path = self.check_path(environ['PATH_INFO'])
        self.info('%s method - %s' % (request_method.upper(), path))
        
        if path.startswith(ResourceHandler._prefix):
            self.debug('Handling resource due to path %s' % path)
            resource = self.get_resource_handler(path)
            if not resource.exists():
                return self.send_error(404, ('resource %s not found' % resource), response)
            
            return resource.handle(response)
            
        
        path = str(path).replace('/', '.')
        page_path = self._path_pattern % path
        mod = None
        try:
            mod = __import__(page_path, globals(), locals(), ['Page'])
        except:
            pass
        
        if mod is None:
            return self.send_error(404, 'Could not find page %s' % path, response)
            
        klass = getattr(mod, 'Page')
        if not klass:
            return self.send_error(500, 'Page file %s does not contains a Page class' % page_path, response)
        
        self.debug('Creating instance of class %s' % klass)
        instance = klass()
        if not instance:
            return self.send_error(500, 'Could not create instace for page %s' % page_path, response)
        
        the_method = 'do_' + request_method
        
        if not hasattr(instance, the_method):
            return self.send_error(500, 'Object %s does not have a method %s' % (instance, request_method), response)
        
        try:
            method = getattr(instance, the_method)
            if params is None:
                return method(environ, response)
            else:
                return method(environ, params, response)
                
        except Exception, e:
            return self.send_error(500, e.message, response)
    
    
    def check_path(self, path):
        p = os.path.basename(path)
        if not p:
            return 'home'
        
        filename = os.path.splitext(p)[0]
        extension = os.path.splitext(p)[1]
        if not extension:
            return filename
        
        return 'res:%s' % path
    
    
    def send_error(self, code, message, response):
        error_message = '%d %s' % (code, message)
        self.error('Sending error %s' % error_message)
        response(error_message, self._create_headers())
        return 'ERROR: %s ' % error_message
    
    
    def _create_headers(self, headers={}):
        response_headers = [('Content-type','text/html; charset=UTF-8')]
        for header in headers:
            response_headers.append(header)
            response_headers.append(headers[header])
        
        return response_headers
    
    
    def get_resource_handler(self, res):
        if not self._resources.has_key(res):
            self._resources[res] = ResourceHandler(res, self._resource_path)
            
        return self._resources[res]
            
            
            
class ResourceHandler(Loggable):
    
    _prefix = 'res:'
    _content_type = None
    _open_as = None
    _file = None
    _extension = None
    _exists = False
    
    def __init__(self, res, resource_path, content_type=None, open_as=''):
        self.debug('Creating ResourceHandler Instance for resource %s' % res)
        
        resource = str(res).replace(ResourceHandler._prefix, '')
        resource = os.path.basename(resource)
        
        self._content_type = content_type
        self._open_as = open_as
        
        self._file = os.path.join(resource_path, resource)
        self._extension = str(os.path.splitext(self._file)[1]).lower()
        self._exists = os.path.exists(self._file)

        self.debug('Resource %s file is %s' % (resource, self._file))
        self.debug('Resource %s exists: %s' % (resource, self._exists))
        
        
    def exists(self):
        return self._exists
    
    
    def handle(self, response):
        self.debug('Handling resource %s' % self._file)
        
        (content_type, open_as) = self._get_content_type()
        if not content_type:
            raise UnknownContentTypeException(self._extension)
        
        headers = [("Content-type", content_type)]
        response("200 OK", headers)

        open_mode = 'r%s' % open_as
        
        file = open(self._file, open_mode)
        
        return file.readlines()
    

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
