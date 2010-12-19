
import os
from serve.log.loggable import Loggable


class RequestHandler(Loggable):
    
    _resources = {}
    _resource_path = None
    _web_path = None
    
    _components = None
    
    
    def __init__(self, path):
        self.info('Request Handler started')
        self._resource_path = os.path.join(path, 'resources')
        self._web_path = os.path.join(path, 'web')
    
    
    
    def do_get(self, environ, response, components={}):
        self.info('Invoking get method')
        self._components = components
        return self.handle_method('get', environ, response)
    
    
    
    def do_post(self, environ, params, response, components={}):
        self.info('Invoking post method')
        self.debug('POST parameters:')
        if params:
            for param in params:
                self.debug("%s = %s" % (param, params[param]))
            
        self._components = components
        return self.handle_method('post', environ, response, params)
    
        
    
    def handle_method(self, request_method, environ, response, params=None):
        #for e in environ:
        #    self.debug('ENV %s = %s' % (e, environ[e]))
        
        request_path = environ['PATH_INFO']
        if request_path == '/' or not request_path:
            request_path = '/home'
            
        self.info('%s method - %s' % (request_method.upper(), request_path))
 
        resource_path = self._resource_path
        web_path = self._web_path
        
        path_options = str(request_path).split('/')
        walked_path = ''
        try:
            for name in path_options:
                if not name:
                    continue
                
                walked_path += '/' + name
                resource_path = os.path.join(resource_path, name)
                web_path = os.path.join(web_path, name)
                
                if self.is_python_file(web_path):
                    self.debug('Found file %s, loading Page' % web_path)
                    
                    path_params = request_path.replace(walked_path, '')
                    environ['PATH_PARAMS'] = path_params
                    
                    instance = self.create_instance(web_path)
                    the_method = 'do_' + request_method
                    if not hasattr(instance, the_method):
                        raise ServerException(501, \
                                              'Object %s does not have a method %s' % \
                                                (instance, request_method))
                        # NOT IMPLEMENTED
                        
                    try:
                        method = getattr(instance, the_method)
                        if params is None:
                            return method(environ, response)
                        else:
                            return method(environ, params, response)
                        
                    except Exception, e:
                        raise ServerException(500, '%s ERROR - %s' % 
                                              (request_method.upper(), e.message))
                    
                elif self.is_resource_file(resource_path):
                    self.debug('Handling resource %s' % resource_path)
                    resource = self.get_resource_handler(resource_path)
                    return resource.handle(response)
                
                else:
                    continue
                        
            raise ServerException(404, 'Could not find resource %s' % request_path)
            # NOT FOUND
        
        except ServerException, e:
            return self.send_error(e.code, e.message, response)
        
        except Exception, e:
            return self.send_error(500, e.message, response)
            # UNKNOWN ERROR
    
    
    def is_python_file(self, file):
        basename = os.path.basename(file)
        basepath = os.path.dirname(file)
        (filename, extension) = os.path.splitext(basename)
        
        if not extension:
            extension = '.py'
        
        py_file = os.path.join(basepath, filename + extension)
        
        return os.path.isfile(py_file)
    
        
    def is_resource_file(self, file):
        return os.path.isfile(file)
    
    
    def create_instance(self, page_path):
        self.debug('Importing module path %s' % page_path)
        
        class_path = os.path.splitext(page_path)[0]
        class_path = class_path.replace(self._web_path, '')
        class_path = class_path.replace('/', '.')
        class_path = 'web' + class_path
        self.debug('Importing module path %s' % class_path)
        
        
        mod = None
        try:
            mod = __import__(class_path, globals(), locals(), ['Page'])
        except:
            self.debug('Import error...')
        
        if mod is None:
            raise ServerException(501, 'Could not load module %s' % page_path)
            #  NOT IMPLEMENTED
            
        klass = getattr(mod, 'Page')
        if not klass:
            raise ServerException(501, 'Module %s does not contains a Page class' % page_path)
            #  NOT IMPLEMENTED
        
        self.debug('Creating instance of class %s' % klass)
        
        for component in self._components:
            self.debug('COMPONENT %s = %s' % (component, self._components[component]))
        
        return klass(self._components)

        
    
    def send_error(self, code, message, response):
        self.error('Sending error \'%s\' %s' % (code, message))
        error_message = '%d %s' % (code, message)
        response(error_message, self._create_headers())
        return 'ERROR: %s ' % message
    
    
    
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
    
    _content_type = None
    _open_as = None
    _file = None
    _extension = None
    
    def __init__(self, res, resource_path, content_type=None, open_as=''):
        self.debug('Creating ResourceHandler Instance for resource %s' % res)
        
        resource = os.path.basename(res)
        
        self._content_type = content_type
        self._open_as = open_as
        
        self._file = os.path.join(resource_path, resource)
        self._extension = str(os.path.splitext(self._file)[1]).lower()

        self.debug('Resource %s file is %s' % (resource, self._file))
        
        
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



class ServerException(Exception):
    
    def __init__(self, code, message):
        Exception.__init__(self)
        self.code = int(code)
        self.message = message
