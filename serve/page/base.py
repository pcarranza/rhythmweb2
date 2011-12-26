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
    
    
    def pre_render_template(self):
        self.debug('PRE Rendering template %s' % self.name())
    
    
    def _render_template(self, node):
        self.pre_render_template()
        self.debug('Rendering template %s' % self.name())
        return self.render_template(node)
    
    
    def render_template(self, node):
        '''
        Must be implemented in inheritor object 
        '''
        raise NotImplementedError
    
    
    def create_template(self, html):
        self.debug('Creating template for component %s' % self.name())
        return Template(self._render_template, html)
    
    
    


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
            self.debug('Template %s rendered bad, sending ERROR response: %s' % (self.name(), e))
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
