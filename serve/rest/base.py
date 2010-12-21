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
    
    
    def do_post(self, environ, params, response):
        self._parameters = params
        self._environ = environ
        
        try:
            return self._return_ok(self.post(), response)
            
        except ServerException, e:
            response('%d %s' % (e.code, e.message), self.do_headers())
            return e.message
    
    
    
    
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
            response('200 OK', self.do_headers(headers))
            json = value.parse()
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
    
    