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

from serve.rest.json import JSon
from serve.request import ServerException
from serve.log.loggable import Loggable

class BaseRest(Loggable):
    
    __environ = None
    __parameters = None
    __path_params = None
    __components = None
    
    def __init__(self, components):
        self.__components = components
        
    
    def __do_headers(self, headers=[]):
        if not headers:
            headers.append(('Content-type','text/html; charset=UTF-8'))
        
        return headers
    
    
    def do_get(self, environ, response):
        self.__environ = environ
        self.parse_path_parameters()
        
        try:
            return_value = self.get()
            self.debug('GET Method executed OK, sending ok response')
            return self.__return_ok(return_value, response)
        
        except ServerException, e:
            response('%d %s' % (e.code, e.message), self.__do_headers())
            return e.message
    
        except Exception, e:
            self.error('Unknown exception when executing GET method: %s' % e)
            response('%d %s' % (500, e), self.__do_headers())
            return '%d %s' % (500, e)
        
    
    def do_post(self, environ, post_params, response):
        self.__parameters = post_params
        self.__environ = environ
        self.parse_path_parameters()
        
        try:
            return_value = self.post()
            self.debug('POST Method executed OK, sending ok response')
            return self.__return_ok(return_value, response)
            
        except ServerException, e:
            response('%d %s' % (e.code, e.message), self.__do_headers())
            return e.message
    
        except Exception, e:
            self.error('Unknown exception when executing GET method: %s' % e)
            response('%d %s' % (500, e), self.__do_headers())
            return '%d %s' % (500, e)
    
    
    
    def __return_ok(self, value, response):
        if value is None:
            return self.__do_page_not_found(response)
        
        if isinstance(value, JSon):
            headers = []
            headers.append(('Content-type','application/json; charset=UTF-8'))
            headers.append(('Cache-Control: ', 'no-cache; must-revalidate'))
            json = value.parse()
            response('200 OK', self.__do_headers(headers))
            self.debug('Returning JSON: %s' % json)
            return json
        
        response('200 OK', self.__do_headers())
        return str(value)

        
    def parse_path_parameters(self):
        path_params = self.__environ['PATH_PARAMS']
        
        querystring_params = []
        if path_params:
            params = str(path_params).split('/')
            for param in params:
                if param:
                    querystring_params.append(param)
                    
        self.__path_params = querystring_params
        
            
    def __do_page_not_found(self, response):
        response('404 NOT FOUND', self.__do_headers())
        return self.__not_found()
    
    
    def __not_found(self):
        return 'Page not found'
    
    
    def get(self):
        raise ServerException(405, 'method GET not allowed')
    
    
    def post(self):
        raise ServerException(405, 'method POST not allowed')
    
    
    
    def unpack_value(self, value):
        if type(value) is dict:
            self.trace('Value is as dictionary, returning dictionary')
            return value
            
        elif type(value) is list:
            if len(value) == 1:
                self.trace('Value was packed as 1 element list')
                svalue = value[0]
                if type(svalue) is str:
                    svalue = svalue.strip()
                    self.trace('Value "%s" is a string, returning stripped' % svalue)
                else:
                    self.trace('Value has type "%s", returning value' % type(svalue))
                    
                return svalue
            
            else:
                self.trace('Value is a list of %d elements, returning list' % len(value))
                return value
            
        else:
            self.trace('Value has type "%s", returning value' % type(value))
            return value


    def pack_as_list(self, value):
        if type(value) is list:
            return value
        elif type(value) is dict:
            return_value = []
            for v in value:
                return_value.append(value[v])
            return return_value
        elif type(value) is str and ',' in value:
            return value.split(',')
        else:
            return [value]
    
    
    def get_component(self, key):
        self.trace('Obtaining component %s' % key)
        
        if not self.__components:
            raise Exception('No components are loaded')
        
        if not self.__components.has_key(key):
            raise Exception('Components dictionary does not contains key "%s"' % key)
        
        return self.__components[key]
        

    def get_environment(self):
        return self.__environ

    
    def get_parameters(self):
        return self.__parameters
    
    
    def get_path_parameters(self):
        return self.__path_params
    
    
    def has_parameter(self, key):
        if not self.__parameters:
            return False
        
        return self.__parameters.has_key(key)
    
    
    def get_parameter(self, key, required=False):
        if not self.has_parameter(key):
            if required:
                raise ServerException(400, 'Bad request, no "%s" parameter' % key)
            else:
                return None
        
        try:
            param = self.__parameters[key]
            param = self.unpack_value(param)
            return param
        except:
            raise ServerException(500, 'Could not unpack post parameter %d' % key)
    
    
    def has_post_parameters(self):
        if self.__parameters is None:
            return False
        
        if not self.__parameters:
            return False
        
        if len(self.__parameters) == 0:
            return False
        
        return True
    
    
    def has_path_parameters(self):
        if self.__path_params is None:
            return False
        
        if not self.__path_params:
            return False
        
        if len(self.__path_params) == 0:
            return False
        return True
    
    
    def get_parameters_size(self):
        if not self.__parameters:
            return 0
        
        return len(self.__parameters)
    
    
    def get_path_parameters_size(self):
        if not self.__path_params:
            return 0
        
        return len(self.__path_params)
    
    
    def get_path_parameter(self, index):
        if not self.__path_params:
            self.warn('No path param with index %d (empty path params)' % index)
            return None
        
        if self.get_path_parameters_size() < index + 1:
            self.warn('No path param with index %d' % index)
            return None
        
        try:
            param = self.__path_params[index]
            param = self.unpack_value(param)
            return param
        except:
            raise ServerException(500, 'Could not unpack path parameter %d' % index)
        