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

import os
import cgi
import re

from serve.request import ResourceHandler, ServerException

import logging
log = logging.getLogger(__name__)

class CGIApplication(object):

    __app_name = None
    __resource_path = None
    __web_path = None
    __components = None

    def __init__(self, app_name, path, components):
        try:
            log.debug('%s CGI Application started' % app_name)

            self.__web_path = os.path.join(path, 'web')
            self.__components = components
            self.__app_name = app_name

            resource_path = os.path.join(path, 'resources')
            self.__resource_path = resource_path
        except:
            log.error('Exception intializing application', exc_info=True)

    def handle_request(self, environ, response):
        method = environ['REQUEST_METHOD']
        log.debug('Handling method %s' % method)
        def do_return(value):
            if type(value) is str:
                return bytes(value, 'UTF-8')
            return value

        try:
            return_value = ''
            if method == 'GET':
                return_value = self.do_get(environ, response)
                yield do_return(return_value)

            elif method == 'POST':
                params = self.parse_post(environ)
                if params is None:
                    log.debug('No parameters in POST method')
                decoded_params = {}
                for key in params:
                    decoded_params[key.decode('UTF-8')] = [value.decode('UTF-8') for value in params[key]]
                return_value = self.do_post(environ, decoded_params, response)
                yield do_return(return_value)

            else:
                self.send_error(
                    500,
                    '%s Not implemented' % method,
                    response)

        except Exception as e:
            log.error('Exception handling request', exc_info=True)
            yield self.send_error(
                 500,
                 '%s Unknown exception' % e,
                 response)

    def parse_post(self, environ):
        log.debug('Parsing post parameters')
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

    def do_get(self, environ, response):
        log.debug('Invoking get method')
        return self.handle_method('get', environ, response)

    def do_post(self, environ, params, response):
        log.debug('Invoking post method')
        log.debug('POST parameters:')
        if params:
            for param in params:
                log.debug("   %s = %s" % (param, params[param]))
        return self.handle_method('post', environ, response, params)


    def get_resource_path(self, environ):
        config = self.__components['config']
        theme_key = 'theme'
        if 'HTTP_USER_AGENT' in environ:
            agent = environ['HTTP_USER_AGENT']
            if re.search('(Android|iPhone)', agent):
                theme_key = 'theme.mobile'
        theme = config.get_string(theme_key)
        resource_path = os.path.join(self.__resource_path, theme)
        return resource_path

    def handle_method(self, request_method, environ, response, params=None):
        log.debug('-------------------------------------')
        log.debug('ENVIRONMENT for method %s: ' % request_method)
        for e in sorted(environ):
            log.debug('   %s = %s' % (e, environ[e]))
        log.debug('-------------------------------------')
        request_path = environ['PATH_INFO']
        if not request_path or request_path == '/':
            request_path = '/index.html'
        if not request_path.startswith('/'):
            request_path = '/' + request_path
        log.debug('handling %s method - path: %s' % (request_method.upper(), request_path))

        resource_path = self.get_resource_path(environ)
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
                    log.debug('Found file %s, loading "Page" class' % web_path)

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

                    except Exception as e:
                        raise ServerException(500, '%s ERROR - %s' %
                                              (request_method, e.message))

                elif self.is_resource_file(web_path):
                    log.debug('Handling web resource %s' % web_path)
                    resource = self.get_resource_handler(web_path)
                    return resource.handle(response, environ)

                elif self.is_resource_file(resource_path):
                    log.debug('Handling file resource %s' % resource_path)
                    resource = self.get_resource_handler(resource_path)
                    return resource.handle(response, environ)

                else:
                    continue

            log.debug('404 - Could not find resource %s' % request_path)
            raise ServerException(404, 'Could not find resource %s' % request_path)
            # NOT FOUND

        except ServerException as e:
            log.error('Exception handling method %s' % request_method, exc_info=True)
            return self.send_error(e.code, e.message, response)

        except Exception as e:
            log.error('Exception handling method %s' % request_method, exc_info=True)
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
        log.debug('Importing module path %s' % page_path)

        class_path = os.path.splitext(page_path)[0]
        class_path = class_path.replace(self.__web_path, '')
        class_path = class_path.replace('/', '.')
        class_path = 'web' + class_path
        log.debug('Importing class path %s' % class_path)

        mod = None
        try:
            mod = __import__(class_path, globals(), locals(), ['Page'])
        except Exception as e:
            log.warn('Import error for file %s: %s' % (class_path, e))

        if mod is None:
            raise ServerException(501, 'Could not load module %s' % page_path)
            #  NOT IMPLEMENTED

        klass = getattr(mod, 'Page')
        if not klass:
            raise ServerException(501, 'Module %s does not contains a Page class' % page_path)
            #  NOT IMPLEMENTED

        log.debug('Creating instance of class "%s" with components:' % klass)
        for component in self.__components:
            log.debug('   %s = %s' % (component, self.__components[component]))

        return klass(self.__components)

    def send_error(self, code, message, response):
        log.error('Returning error \'%s\' %s' % (code, message), exc_info=True)
        error_message = '%d %s' % (code, message)
        response(error_message, self.__default_headers())
        return 'ERROR: %s' % message

    def get_resource_handler(self, resource):
        return ResourceHandler(resource) # dont cache

    def __default_headers(self, headers=[]):
        if not headers:
            headers = [('Content-type', 'text/html; charset=UTF-8')]
        return headers
