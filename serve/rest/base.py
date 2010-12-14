from serve.rest.json import JSon

class BaseRest():
    
    _environ = None
    _parameters = None
    
    def do_headers(self, headers={}):
        response_headers = [('Content-type','text/html; charset=UTF-8')]
        for header in headers:
            response_headers.append(header)
            response_headers.append(headers[header])
        
        return response_headers
    
    
    def do_get(self, environ, response):
        self._environ = environ
        
        return_value = self.get(environ)
        
        if return_value is None:
            response('404 NOT FOUND', self.do_headers())
        
        if type(return_value) is JSon:
            return return_value.write()
        
        return str(return_value)
    
    def do_post(self, environ, params, response):
        self._parameters = params
        self._environ = environ
        