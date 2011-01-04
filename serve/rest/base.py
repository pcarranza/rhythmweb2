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
    
    _environ = None
    _parameters = None
    _path_params = None
    _components = None
    
    def __init__(self, components):
        self._components = components
        
    
    def do_headers(self, headers=[]):
        if not headers:
            headers.append(('Content-type','text/html; charset=UTF-8'))
        
        return headers
    
    
    def do_get(self, environ, response):
        self._environ = environ
        self.parse_path_parameters()
        
        try:
            return self._return_ok(self.get(), response)
        
        except ServerException, e:
            response('%d %s' % (e.code, e.message), self.do_headers())
            return e.message
    
        except Exception, e:
            self.error(e)
            response('%d %s' % (500, e), self.do_headers())
            return '%d %s' % (500, e)
        
    
    def do_post(self, environ, params, response):
        self._parameters = params
        self._environ = environ
        self.parse_path_parameters()
        
        try:
            return self._return_ok(self.post(), response)
            
        except ServerException, e:
            response('%d %s' % (e.code, e.message), self.do_headers())
            return e.message
    
        except Exception, e:
            self.error(e)
            response('%d %s' % (500, e), self.do_headers())
            return '%d %s' % (500, e)
    
    
    
    def _return_ok(self, value, response):
        if value is None:
            return self._do_page_not_found(response)
        
        # header('Cache-Control: no-cache, must-revalidate');
        # header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');
        # header('Content-type: application/json');
        
        if isinstance(value, JSon):
            headers = []
            headers.append(('Content-type','application/json; charset=UTF-8'))
            headers.append(('Cache-Control: ', 'no-cache; must-revalidate'))
            json = value.parse()
            response('200 OK', self.do_headers(headers))
            self.debug('Returning JSON: %s' % json)
            return json
        
        response('200 OK', self.do_headers())
        return str(value)

        
    def parse_path_parameters(self):
        path_params = self._environ['PATH_PARAMS']
        
        querystring_params = []
        if path_params:
            params = str(path_params).split('/')
            for param in params:
                if param:
                    querystring_params.append(param)
            self._path_params = querystring_params
            
            
    def _do_page_not_found(self, response):
        response('404 NOT FOUND', self.do_headers())
        return self.not_found()
    
    
    def not_found(self):
        return 'Page not found'
    
    
    def get(self):
        raise ServerException(405, 'method GET not allowed')
    
    
    def post(self):
        raise ServerException(405, 'method POST not allowed')
    
    
    
    def unpack_value(self, value):
        if type(value) is dict:
            svalue = ''.join(value)
            self.debug('Value \"%s\" was packed as dictionary' % svalue)
            
        elif type(value) is list:
            if len(value) == 1:
                self.debug('Value \"%s\" was packed as 1 element list' % value[0])
                return value[0]
            
            svalue = ''.join(value)
            self.debug('Value \"%s\" was packed as list' % svalue)
        else:
            svalue = str(value)
            self.debug('Value \"%s\" was packed as plain string' % svalue)
            
        return svalue.strip()


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
