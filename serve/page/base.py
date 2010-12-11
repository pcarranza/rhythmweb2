from serve.log.loggable import Loggable
from serve.template.HTMLTemplate import Template
import os


class Component(Loggable):
    '''
    Represents an abstract html component, has methods to find html file and load it
    '''
    
    _template = None
    _path = None

    def __init__(self, file):
        self.set_path(file)


    def name(self):
        raise NotImplementedError
        
    
    def set_path(self, file):
        '''
        Sets the absolute file path of current object, used to get html file
        '''
        self._path = os.path.abspath(file)
    

    def load_html(self):
        '''
        Loads the html file related to the current object and returns the html itself
        '''
        
        if not self._path:
            raise ComponentPathNotImplemented()

        self.debug("Loading html file %s for component %s" % (self._path, self.name()))
        
        dir = os.path.dirname(self._path)
        file = os.path.basename(self._path)
        filename = os.path.splitext(file)[0] + '.html'
        
        html_file = os.path.join(dir, filename)
        if not os.path.exists(html_file):
            raise HtmlFileNotFoundException(html_file)
        
        self.debug('Loading html %s for component %s' % (html_file, self.name()))
        
        return open(html_file, 'r').read()


    def render(self, environ):
        '''
        Must be implemented in inheritor object 
        '''
        raise NotImplementedError
    
    
    def render_template(self, node):
        '''
        Must be implemented in inheritor object 
        '''
        raise NotImplementedError
    
    
    def create_template(self, html):
        self.debug('Creating template for component %s' % self.name())
        return Template(self.render_template, html)
    
    
    


class BasePage(Component):
    '''
    Abstract base page, provides the overridable method "name()" 
    which must be implemented in the inheritor object 
    '''
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
        template = self.create_template(self.load_html())
        self.debug('Getting template %s' % self.name())
        try:
            html = template.render()
            response('200 OK', self.do_headers())
            self.debug('Template %s rendered ok, sending OK response' % self.name())
            return html
        except Exception, e:
            self.debug('Template %s rendered bad, sending ERROR response' % self.name())
            response('500 ERROR', self.do_headers())
            return e
    
    
    def do_post(self, environ, params, response):
        self._parameters = params
        self._environ = environ
        self.debug('Processing post in BasePage for component %s' % self.name())
        self.post()
        return self.do_get(environ, response)
        
    
        
    def post(self):
        self.warning('No actual posting... override post in ' + self.name())


    
    
class BasePanel(Component):
    '''
    Abstract panel, provides the method render(self) 
    which must be implemented in the inheritor object 
    '''
    
    def render(self):
        template = self.create_template(self.load_html())
        self.debug('Rendering panel %s' % self.name())
        return template.render()
    

    
class HtmlFileNotFoundException(Exception):
    
    filename = None
    
    def __init__(self, filename):
        Exception.__init__(self)
        self.filename = filename
        self.message = 'HTML File %s not found' % filename


class ComponentPathNotImplemented(Exception):
    
    def __init__(self):
        Exception.__init__(self)
        self.message = 'Implement Page class constructor and invoke set_path(__file__)'