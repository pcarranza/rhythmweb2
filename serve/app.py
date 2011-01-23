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

from serve.log.loggable import Loggable
import os
import cgi
from serve.request import ResponseWrapper, ResourceHandler, ServerException

class CGIApplication(Loggable):
    
    __app_name = None
    __resource_path = None
    __web_path = None
    __components = None

    
    def __init__(self, app_name, path, components):
        self.debug('%s CGI Application started' % app_name)
        self.__resource_path = os.path.join(path, 'resources')
        self.__web_path = os.path.join(path, 'web')
        self.__components = components
        self.__app_name = app_name
    
    
    def handle_request(self, environ, response):
        
        method = environ['REQUEST_METHOD']
        
        self.trace('Handling method %s' % method)
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
            
            return self.send_error(
                 500, 
                 '%s Not implemented' % method, 
                 response)
            
        except Exception, e:
            return self.send_error(
                 500, 
                 '%s Unknown exception' % e, 
                 response)
            
            
    
            
            
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

    
    
    def __do_get(self, environ, response):
        self.trace('Invoking get method')
        
        wrapper = ResponseWrapper(environ, response)
        return_value = self.handle_method('get', environ, wrapper.response)
        return wrapper.wrap(return_value)
    
    
    def __do_post(self, environ, params, response):
        self.trace('Invoking post method')
        self.trace('POST parameters:')
        if params:
            for param in params:
                self.trace("   %s = %s" % (param, params[param]))
        
        # gzipping POST does not works, for some reason... 
        # wrapper = ResponseWrapper(environ, response)
        return self.handle_method('post', environ, response, params)
        # return wrapper.wrap(return_value)
    
        
    def handle_method(self, request_method, environ, response, params=None):
        
        self.trace('-------------------------------------')
        self.trace('ENVIRONMENT for method %s: ' % request_method)
        for e in environ:
            self.trace('   %s = %s' % (e, environ[e]))
        self.trace('-------------------------------------')
        
        request_path = environ['PATH_INFO']
        
        if not request_path or request_path == '/':
            request_path = '/index.html'
            
        if not request_path.startswith('/'):
            request_path = '/' + request_path
            
        self.debug('%s method - path: %s' % (request_method.upper(), request_path))
 
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
                    self.trace('Found file %s, loading "Page" class' % web_path)
                    
                    path_params = request_path.replace(walked_path, '')
                    environ['PATH_PARAMS'] = path_params
                    
                    instance = self.create_instance(web_path)
                    the_method = 'do_' + request_method
                    if not hasattr(instance, the_method):
                        raise ServerException(501, \
                                              'Object %s does not have a %s method' % \
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
                    self.trace('Handling resource %s' % web_path)
                    resource = self.get_resource_handler(web_path)
                    return resource.handle(response, environ)

                elif self.is_resource_file(resource_path):
                    self.trace('Handling resource %s' % resource_path)
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
        self.trace('Importing module path %s' % page_path)
        
        class_path = os.path.splitext(page_path)[0]
        class_path = class_path.replace(self.__web_path, '')
        class_path = class_path.replace('/', '.')
        class_path = 'web' + class_path
        self.trace('Importing class path %s' % class_path)
        
        mod = None
        try:
            mod = __import__(class_path, globals(), locals(), ['Page'])
        except Exception, e:
            self.warn('Import error for file %s: %s' % (class_path, e))
        
        if mod is None:
            raise ServerException(501, 'Could not load module %s' % page_path)
            #  NOT IMPLEMENTED
            
        klass = getattr(mod, 'Page')
        if not klass:
            raise ServerException(501, 'Module %s does not contains a Page class' % page_path)
            #  NOT IMPLEMENTED
        
        self.trace('Creating instance of class "%s" with components:' % klass)
        for component in self.__components:
            self.trace('   %s = %s' % (component, self.__components[component]))
        
        return klass(self.__components)

        
    def send_error(self, code, message, response):
        self.error('Returning error \'%s\' %s' % (code, message))
        error_message = '%d %s' % (code, message)
        response(error_message, self.__default_headers())
        return 'ERROR: %s' % message
    
    
    def get_resource_handler(self, resource):
        return ResourceHandler(resource) # dont cache
    
    
    def __default_headers(self, headers=[]):
        if not headers:
            headers = [('Content-type', 'text/html; charset=UTF-8')]
            
        return headers



        