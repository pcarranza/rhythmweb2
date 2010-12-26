
import os
import StringIO
from serve.log.loggable import Loggable
from datetime import timedelta, datetime
from gzip import GzipFile

class RequestHandler(Loggable):
    
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
        for e in environ:
            self.debug('ENV %s = %s' % (e, environ[e]))
        
        request_path = environ['PATH_INFO']
        
        if not request_path or request_path == '/':
            request_path = '/index.html'
            
        if not request_path.startswith('/'):
            request_path = '/' + request_path
            
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
                                              (request_method, e.message))
                    
                elif self.is_resource_file(web_path):
                    self.debug('Handling resource %s' % web_path)
                    resource = self.get_resource_handler(web_path)
                    return resource.handle(response, self.is_accept_gzip(environ))

                elif self.is_resource_file(resource_path):
                    self.debug('Handling resource %s' % resource_path)
                    resource = self.get_resource_handler(resource_path)
                    return resource.handle(response, self.is_accept_gzip(environ))
                    
                else:
                    continue
                        
            raise ServerException(404, 'Could not find resource %s' % request_path)
            # NOT FOUND
        
        except ServerException, e:
            return self.send_error(e.code, e.message, response)
        
        except Exception, e:
            return self.send_error(500, e.message, response)
            # UNKNOWN ERROR

    
    def is_accept_gzip(self, env):
        if 'HTTP_ACCEPT_ENCODING' in env:
            accept = env['HTTP_ACCEPT_ENCODING']
            accept = str(accept).split(',')
            if 'gzip' in accept:
                return True
            
        return False
    
    
    def is_python_file(self, file):
        basename = os.path.basename(file)
        basepath = os.path.dirname(file)
        (filename, extension) = os.path.splitext(basename)
        
        if not extension:
            extension = '.py'
        elif not extension == '.py':
            return False
        
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
    
    
    def _create_headers(self, headers=[]):
        if not headers:
            headers = [('Content-type', 'text/html; charset=UTF-8')]
            
        return headers
    
    
    def get_resource_handler(self, resource):
        return ResourceHandler(resource) # dont cache
    

            
class ResourceHandler(Loggable):
    
    _content_type = None
    _open_as = None
    _file = None
    _extension = None
    
    def __init__(self, resource, content_type=None, open_as=''):
        self.debug('Creating ResourceHandler Instance for resource %s' % resource)
        
        self._content_type = content_type
        self._open_as = open_as
        
        self._file = resource
        self._extension = str(os.path.splitext(self._file)[1]).lower()

        self.debug('Resource %s file is %s' % (resource, self._file))
        
        
    def handle(self, response, accept_gzip=False):
        self.debug('Handling resource %s' % self._file)
        
        (content_type, open_as) = self._get_content_type()
        if not content_type:
            raise UnknownContentTypeException(self._extension)
        
#        size = os.path.getsize(self._file)
        mtime = os.path.getmtime(self._file)
        mtime = datetime.fromtimestamp(mtime)
        expiration = datetime.now() + timedelta(days=365)

#     ('Content-Length', str(size)), \
        
        headers = [("Content-type", content_type), \
                   ('Cache-Control', 'public'), \
                   ('Last-Modified', mtime.ctime()), \
                   ('Expires', expiration.ctime())]
        
        if accept_gzip:
            headers.append(("Content-Encoding", "gzip"))
            headers.append(("Vary", "Accept-Encoding"))
        
        for header in headers:
            self.debug('%s=%s' % (header[0], header[1]))
        
        response("200 OK", headers)

        open_mode = 'r%s' % open_as
        
        file = open(self._file, open_mode)
        
        if accept_gzip:
            data = "".join(file.readlines())
            return [self.gzip_string(data, 8)]
        else:
            return file.readlines()
    

    def _get_content_type(self):
        if not self._content_type:
            (self._content_type, self._open_as) = self._content_type_by_ext(self._extension)
        
        self.debug('Returning content type %s' % self._content_type)
        return (self._content_type, self._open_as)
    
    
    def _content_type_by_ext(self, ext):
        if ext == '.css':
            return ('text/css', 't')
        if ext == '.htm':
            return ('text/html', 't')
        if ext == '.html':
            return ('text/html', 't')
        if ext == '.gif':
            return ('image/gif', 'b')
        if ext == '.png':
            return ('image/png', 'b')
        if ext == '.jpg':
            return ('image/jpeg', 'b')
        if ext == '.jpeg':
            return ('image/jpeg', 'b')
        if ext == '.ico':
            return ('image/ico', 'b')
        if ext == '.svg':
            return ('image/svg+xml', 't')
        if ext == '.js':
            return ('application/x-javascript', 't')
        
        return ('text/plain', 't')
    
    
    def gzip_string(self, string, compression_level):
        """ The `gzip` module didn't provide a way to gzip just a string.
            Had to hack together this. I know, it isn't pretty.
        """
        fake_file = StringIO.StringIO()
        gz_file = GzipFile(None, 'wb', compression_level, fileobj=fake_file)
        gz_file.write(string)
        gz_file.close()
        return fake_file.getvalue()


class UnknownContentTypeException(Exception):
    
    def __init__(self, ext):
        Exception.__init__(self)
        self.message = 'Unknown content type %s' % ext


class ServerException(Exception):
    
    def __init__(self, code, message):
        Exception.__init__(self)
        self.code = int(code)
        self.message = message
