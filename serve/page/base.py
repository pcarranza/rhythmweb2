from serve.log.loggable import Loggable
from serve.template.HTMLTemplate import Template
import os


class Component(Loggable):
    '''
    Represents an abstract html component, has methods to find html file and load it
    '''
    
    _request = None
    _template = None
    _path = None

    def __init__(self, request, file):
        '''
        Constructor, requires that inherithing class sends __file__ as file parameter, 
        also as the request which will be received from the invoker server object
        '''
        self._request = request
        self.set_path(file)
    
    
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
        
        dir = os.path.dirname(self._path)
        file = os.path.basename(self._path)
        filename = os.path.splitext(file)[0] + '.html'
        
        html_file = os.path.join(dir, filename)
        if not os.path.exists(html_file):
            raise HtmlFileNotFoundException(html_file)
        
        self.debug('Loading html component %s' % html_file)
        
        return open(html_file, 'r').read()


    def render(self):
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
        return Template(self.render_template, html)
    
    
    


class BasePage(Component):
    '''
    Abstract base page, provides the overridable method "name()" 
    which must be implemented in the inheritor object 
    '''
    def name(self):
        raise NotImplementedError
    
    
    def do_headers(self):
        self.debug('Page %s sending code 200' % self.name())
        
        self._request.send_response(200)
        self._request.send_header("Content-type", "text/html")
        self._request.end_headers()
    
    
    def render(self):
        template = self.create_template(self.load_html())
        self.do_headers()
        
        self.debug('Rendering template %s' % self.name())
        return template.render()


    def render_page(self):
        self._request.wfile.write(self.render())

    
    
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