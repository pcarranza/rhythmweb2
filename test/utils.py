import os
from mock import Mock
from io import BytesIO
from collections import defaultdict
from serve.app import CGIApplication

class Stub(object):

    def __init__(self, key=None):
        self.key = key

    def __getattr__(self, name):
        if name == 'id' and self.key:
            return self.key
        return name


def cgi_application():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config = Mock()
    config.get_string.return_value = 'default'
    return CGIApplication(base_path, config)


def environ(path, post_data=None):
    environ = defaultdict(lambda: '')
    environ['PATH_INFO'] = path
    if post_data:
        environ['REQUEST_METHOD'] = 'POST'
        environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        environ['CONTENT_LENGTH'] = len(post_data)
        environ['wsgi.input'] = BytesIO(bytes(post_data, 'UTF-8'))
    else:
        environ['REQUEST_METHOD'] = 'GET'
    return environ

def handle_request(app, env, response):
    result = app.handle_request(env, response)
    if result:
        return ''.join(line.decode('UTF-8') for line in result)
    return ''

