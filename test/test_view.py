
import unittest

from rhythmweb.view import app, route


class TestPathParams(unittest.TestCase):

    def test_parser_finds_one_param(self):
        result = app.route('/test/value')
        self.assertEquals('value', result)

    def test_parser_finds_two_params(self):
        result1, result2 = app.route('/other/route/value1/value2')
        self.assertEquals('value1', result1)
        self.assertEquals('value2', result2)

    def test_route_with_kwargs(self):
        result = app.route('/route/with/kwargs', argument='value')
        self.assertEquals('value', result)

@route('/test/<name>')
def simple_test(name):
    return name

@route('/other/route/<first>/<second>')
def slightly_harder_test(one, two):
    return one, two

@route('/route/with/kwargs')
def route_with_kwargs(**kwargs):
    return kwargs['argument']


class TestMountFilesystem(unittest.TestCase):

    def test_mount_file(self):
        app.mount('./test/acceptance.sh', 'default')
        f = app.get_file('/test/acceptance.sh', 'default')
        self.assertFalse(len(f) == 0)

    def test_mount_path(self):
        app.mount('./test', 'other', ignore='/test')
        f = app.get_file('/bootstrap.sh', 'other')
        self.assertFalse(len(f) == 0)
