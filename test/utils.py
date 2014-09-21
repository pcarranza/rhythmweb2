import os
from mock import Mock
from io import BytesIO
from collections import defaultdict


class Stub(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, name):
        if name in self.kwargs:
            return self.kwargs[name]
        return name

    def __int__(self):
        return self.kwargs.get('id')

    def __str__(self):
        return 'Stub: "{}"'.format(self.kwargs)


class EntryStub(object):

    def __init__(self, key, **kwargs):
        self.key = key
        self.args = kwargs

    def get_ulong(self, name):
        return self.args.get(name, self.key)

    def get_string(self, name):
        return self.args.get(name, name)

    def get_double(self, name):
        return self.args.get(name, 1.0)

    def __str__(self):
        return 'EntryStub key: "{}"'.format(self.key)


class ModelStub(object):

    def __init__(self, *rows):
        self.rows = [[row] for row in rows]
        self.sort_order = None
        self.desc = None

    def __getitem__(self, key):
        return self.rows[key]

    def __iter__(self):
        for row in self.rows:
            yield row

    def set_sort_order(self, sort_order, arg3, desc):
        self.sort_order = sort_order
        self.desc = desc

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

