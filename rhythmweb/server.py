import os
import re
import cgi
import json

from rhythmweb.app import app

import logging
log = logging.getLogger(__name__)

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
default_resource = os.path.join(base_path, 'resources/default')
touch_resource = os.path.join(base_path, 'resources/touch')

app.mount(default_resource, 'default', ignore=default_resource)
app.mount(touch_resource, 'mobile', ignore=touch_resource)

match_mobile = re.compile(r'(Android|iPhone)')

CONTENT_TYPES = {
    'css': 'text/css',
    'htm': 'text/html',
    'html': 'text/html',
    'gif': 'image/gif',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'ico': 'image/ico',
    'svg': 'image/svg+xml',
    'js': 'application/x-javascript',
}

class Server(object):

    def handle_request(self, environ, response):
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/')
        if path == '/':
            path = '/index.html'
        group = 'mobile' if match_mobile.match(environ.get('HTTP_USER_AGENT', '')) else 'default'
        response = Response(response)
        log.debug('Handling request {} {}'.format(method, path))
        try:
            if method == 'GET':
                content = app.get_file(path, group)
                if content:
                    return response.reply_with_file(path, content)
                content = app.route(path)
                if content is None:
                    return response.reply_with_not_found()
                return response.reply_with_json(content)

            if method == 'POST':
                post = self.parse_post_parameters(environ)
                content = app.route(path, **post)
                if content is None:
                    return response.reply_with_not_found()
                return response.reply_with_json(content)

        except ValueError as e:
            return response.reply_with_client_error(e)

        except TypeError:
            return response.reply_with_method_not_allowed(method)

        except ServerError as e:
            return response.reply_with_server_error(e)

    def parse_post_parameters(self, environ):
        parsed = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values=True
        )
        post = {}
        for key in parsed.keys():
            post[key] = parsed[key].value
        return post


class Response(object):

    def __init__(self, function):
        self.function = function

    def reply_with_json(self, content):
        log.debug('Returning json {}'.format(content))
        self.function('200 OK', [
            ('Content-type', 'application/json; charset=UTF-8'), 
            ('Cache-Control: ', 'no-cache; must-revalidate')])
        return [bytes(json.dumps(content), 'UTF-8')]

    def reply_with_not_found(self):
        log.debug('Returning not found')
        self.function('404 NOT FOUND', [
            ('Content-type', 'text/html; charset=UTF-8')])
        return []

    def reply_with_file(self, path, content):
        extension = path.split('.')[-1].lower()
        content_type = CONTENT_TYPES.get(extension, 'text/plain')
        self.function('200 OK', [('Content-type', content_type),
            ('Cache-Control: ', 'no-cache; must-revalidate')])
        log.debug('Returning {} {}={}'.format(path, extension, content_type))
        return content

    def reply_with_client_error(self, e):
        log.debug('Returning bad request')
        self.function('400 Bad Request: {}'.format(e), [
            ('Content-type', 'text/html; charset=UTF-8')])
        return []

    def reply_with_method_not_allowed(self, method):
        log.debug('Error while running method {}'.format(method), exc_info=True)
        self.function('405 method {} not allowed'.format(method), [
            ('Content-type', 'text/html; charset=UTF-8')])
        return []



class ServerError(Exception):
    pass
