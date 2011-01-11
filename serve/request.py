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

import os
import StringIO
from serve.log.loggable import Loggable
from datetime import timedelta, datetime
from gzip import GzipFile

class RequestHandler(Loggable):

    
    __resource_path = None
    __web_path = None
    __components = None

    
    def __init__(self, path):
        self.info('Request Handler started')
        self.__resource_path = os.path.join(path, 'resources')
        self.__web_path = os.path.join(path, 'web')
        
    
    def do_get(self, environ, response, components={}):
        self.info('Invoking get method')
        self.__components = components
        
        wrapper = ResponseWrapper(environ, response)
        return_value = self.handle_method('get', environ, wrapper.response)
        return wrapper.wrap(return_value)
    
    
    def do_post(self, environ, params, response, components={}):
        self.info('Invoking post method')
        self.debug('POST parameters:')
        if params:
            for param in params:
                self.debug("%s = %s" % (param, params[param]))
        
        self.__components = components
        
        # gzipping POST does not works, for some reason... 
        # wrapper = ResponseWrapper(environ, response)
        return self.handle_method('post', environ, response, params)
        # return wrapper.wrap(return_value)
    
        
    def handle_method(self, request_method, environ, response, params=None):
#        ONLY ENABLE IF EXTREME REQUEST DATA DEBUGGING IS NEEDED
#        for e in environ:
#            self.debug('ENV %s = %s' % (e, environ[e]))
        
        request_path = environ['PATH_INFO']
        
        if not request_path or request_path == '/':
            request_path = '/index.html'
            
        if not request_path.startswith('/'):
            request_path = '/' + request_path
            
        self.info('%s method - %s' % (request_method.upper(), request_path))
 
        resource_path = self.__resource_path
        web_path = self.__web_path
        
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
                    return resource.handle(response, environ)

                elif self.is_resource_file(resource_path):
                    self.debug('Handling resource %s' % resource_path)
                    resource = self.get_resource_handler(resource_path)
                    return resource.handle(response, environ)
                    
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
        elif not extension == '.py':
            return False
        
        py_file = os.path.join(basepath, filename + extension)
        
        return os.path.isfile(py_file)
    
        
    def is_resource_file(self, file):
        return os.path.isfile(file)
    
    
    def create_instance(self, page_path):
        self.debug('Importing module path %s' % page_path)
        
        class_path = os.path.splitext(page_path)[0]
        class_path = class_path.replace(self.__web_path, '')
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
        
        for component in self.__components:
            self.debug('COMPONENT %s = %s' % (component, self.__components[component]))
        
        return klass(self.__components)

        
    def send_error(self, code, message, response):
        self.error('Sending error \'%s\' %s' % (code, message))
        error_message = '%d %s' % (code, message)
        response(error_message, self.__default_headers())
        return 'ERROR: %s ' % message
    
    
    def get_resource_handler(self, resource):
        return ResourceHandler(resource) # dont cache
    
    
    def __default_headers(self, headers=[]):
        if not headers:
            headers = [('Content-type', 'text/html; charset=UTF-8')]
            
        return headers
    
    
    
class ResponseWrapper(Loggable):
    
    __headers = None
    __status = None
    
    def __init__(self, environment, response, compression_level=8):
        self.__response = response
        self.__env = environment
        self.__accept_gzip = self.is_accept_gzip()
        self.__compression_level = compression_level
        
        
    def response(self, status, headers):
        self.debug('Responding with wrapper')
        if not headers:
            self.debug('No headers, creating new')
            headers = [('Content-type', 'text/html; charset=UTF-8'), \
                       ('Cache-Control', 'public')]
        
        if self.__accept_gzip:
            self.debug('Client accepts gzip encoding, appendig to headers')
            headers.append(("Content-Encoding", "gzip"))
            headers.append(("Vary", "Accept-Encoding"))
            
        self.__headers = headers
        self.__status = status
    
    
    def wrap(self, return_value):
        if self.__status is None:
            raise ServerException(500, 'No response status was setted')
        
        if self.__headers is None:
            raise ServerException(500, 'No response headers were setted')
        
        if self.__accept_gzip:
            self.debug('GZipping response')        
            value = self.gzip_string(return_value, self.__compression_level)
        else:
            self.debug('Plain response, no gzipping requested')
            value = return_value
            
        length = len(value)
        self.__headers.append(('Content-Length', str(length)))
        
        self.debug('Responding with code %s' % self.__status)
        for header in self.__headers:
            self.debug('   - %s : %s' % tuple(header))
        
        self.__response(self.__status, self.__headers)
        return value
                
        

    def is_accept_gzip(self):
        if 'HTTP_ACCEPT_ENCODING' in self.__env:
            accept = self.__env['HTTP_ACCEPT_ENCODING']
            accept = str(accept).split(',')
            if 'gzip' in accept:
                self.debug('Client accepts gzip encoding')        
                return True
        return False
    
    
    def gzip_string(self, string, compression_level):
        """ The `gzip` module didn't provide a way to gzip just a string.
            Had to hack together this. I know, it isn't pretty.
        """
        fake_file = StringIO.StringIO()
        gz_file = GzipFile(None, 'wb', compression_level, fileobj=fake_file)
        gz_file.write(string)
        gz_file.close()
        return fake_file.getvalue()
        
        
class ResourceHandler(Loggable):
    
    __content_type = None
    __open_as = None
    __file = None
    __extension = None
    
    def __init__(self, resource, content_type=None, open_as=''):
        self.debug('Creating ResourceHandler Instance for resource %s' % resource)
        
        self._content_type = content_type
        self.__open_as = open_as
        
        self.__file = resource
        self.__extension = str(os.path.splitext(self.__file)[1]).lower()

        self.debug('Resource %s file is %s' % (resource, self.__file))
        
        
    def handle(self, response, accept_gzip=False):
        self.debug('Handling resource %s' % self.__file)
        
        (content_type, open_as) = self.__get_content_type()
        if not content_type:
            raise UnknownContentTypeException(self.__extension)
        
        mtime = os.path.getmtime(self.__file)
        mtime = datetime.fromtimestamp(mtime)
        expiration = datetime.now() + timedelta(days=365)

        headers = [("Content-type", content_type), \
                   ('Cache-Control', 'public'), \
                   ('Last-Modified', mtime.ctime()), \
                   ('Expires', expiration.ctime())]
        
        response('200 OK', headers)

        open_mode = 'r%s' % open_as
        
        file = open(self.__file, open_mode)
        
        return ''.join(file.readlines())
    

    def __get_content_type(self):
        if not self.__content_type:
            (self.__content_type, self.__open_as) = self.__content_type_by_ext(self.__extension)
        
        self.debug('Returning content type %s' % self.__content_type)
        return (self.__content_type, self.__open_as)
    
    
    def __content_type_by_ext(self, ext):
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
    
    
class UnknownContentTypeException(Exception):
    
    
    def __init__(self, ext):
        Exception.__init__(self)
        self.message = 'Unknown content type %s' % ext


class ServerException(Exception):
    
    
    def __init__(self, code, message):
        Exception.__init__(self)
        self.code = int(code)
        self.message = message

