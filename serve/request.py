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
import io
from datetime import timedelta, datetime

import logging
log = logging.getLogger(__name__)
 
    
class ResponseWrapper(object):
    
    __headers = None
    __status = None
    
    def __init__(self, environment, response, compression_level=8):
        self.__response = response
        
    def response(self, status, headers):
        log.debug('Responding with wrapper')
        if not headers:
            log.debug('No headers, creating new')
            headers = [('Content-type', 'text/html; charset=UTF-8'), \
                       ('Cache-Control', 'public')]
        
        self.__headers = headers
        self.__status = status
    
    def wrap(self, return_value):
        if self.__status is None:
            raise ServerException(500, 'No response status was setted')
        
        if self.__headers is None:
            raise ServerException(500, 'No response headers were setted')
        
        value = return_value
            
        length = len(value)
        self.__headers.append(('Content-Length', str(length)))
        
        log.debug('Responding with code %s' % self.__status)
        for header in self.__headers:
            log.debug('   %s : %s' % tuple(header))
        
        self.__response(self.__status, self.__headers)
        return value


class ResourceHandler(object):
    
    __content_type = None
    __open_as = None
    __file = None
    __extension = None
    
    def __init__(self, resource, content_type=None, open_as=''):
        try:
            log.debug('Creating ResourceHandler Instance for resource %s' % resource)
            
            self._content_type = content_type
            self.__open_as = open_as
            
            self.__file = resource
            self.__extension = str(os.path.splitext(self.__file)[1]).lower()

            log.debug('Resource %s file is %s' % (resource, self.__file))
        except:
            log.error('Exception initializing resource handler')
        
    def handle(self, response, accept_gzip=False):
        try:
            log.debug('Handling resource %s' % self.__file)
            
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
            
            open_mode = 'r%s' % open_as
            
            with open(self.__file, open_mode) as f:
                response('200 OK', headers)
                return f.read()
        except:
            log.error('Exception handling resource {}'.format(self.__file), exc_info=True)
            return ''

    def __get_content_type(self):
        if not self.__content_type:
            (self.__content_type, self.__open_as) = self.__content_type_by_ext(self.__extension)
        
        log.debug('Returning content type %s' % self.__content_type)
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
