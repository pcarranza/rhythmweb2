
import unittest

from rhythmweb.app import app, route


class TestPathParams(unittest.TestCase):

    def test_parser_finds_one_param(self):
        result = app.route('/test/value')
        self.assertEquals('value', result)

    def test_parser_finds_two_params_with_one_supported_ignores_second(self):
        result = app.route('/test/value1/value2')
        self.assertEquals('value1', result)

    def test_parser_finds_two_params(self):
        result1, result2 = app.route('/other/route/value1/value2')
        self.assertEquals('value1', result1)
        self.assertEquals('value2', result2)

    def test_route_with_kwargs(self):
        result = app.route('/route/with/kwargs', argument='value')
        self.assertEquals('value', result)

    def test_route_with_optional_arguments(self):
        one, two, three, fourth = app.route('/another/one/two/three')
        self.assertEquals('one', one)
        self.assertEquals('two', two)
        self.assertEquals('three', three)
        self.assertIsNone(fourth)

    def test_route_with_two_optional_arguments_works_as_expected(self):
        one, two, three, fourth = app.route('/another/one/two')
        self.assertEquals('one', one)
        self.assertEquals('two', two)
        self.assertIsNone(three)
        self.assertIsNone(fourth)

    def test_route_without_mandatory_argument_returns_none(self):
        self.assertIsNone(app.route('/another/one'))

    def test_parser_with_type_returns_int_and_float_value(self):
        result1, result2 = app.route('/typed/route/1/2.1')
        self.assertEquals(1, result1)
        self.assertEquals(2.1, result2)

    def test_parser_with_type_fails_with_invalid_int(self):
        with self.assertRaises(ValueError):
            app.route('/typed/route/x/2.1')

    def test_parser_with_type_fails_with_invalid_float(self):
        with self.assertRaises(ValueError):
            app.route('/typed/route/1/2.1.3')

@route('/test/<name>')
def simple_test(name):
    return name

@route('/other/route/<first>/<second>')
def slightly_harder_test(one, two):
    return one, two

@route('/route/with/kwargs')
def route_with_kwargs(**kwargs):
    return kwargs['argument']

@route('/another/<first:str>/<second:str>/<third?:str>/<fourth?:str>')
def route_with_optional_path(one, two, three, four):
    return one, two, three, four

@route('/typed/route/<one:int>/<two:float>')
def route_with_type(int_value, float_value):
    return int_value, float_value

class TestMountFilesystem(unittest.TestCase):

    def test_mount_file_finds_file(self):
        app.mount('./test/acceptance.sh', 'default')
        f = app.get_file('/test/acceptance.sh', 'default')
        self.assertFalse(len(f) == 0)

    def test_mount_path_finds_file(self):
        app.mount('./test', 'other', ignore='/test')
        f = app.get_file('/bootstrap.sh', 'other')
        self.assertFalse(len(f) == 0)

    def test_get_invalid_file_returns_none(self):
        app.mount('./test', 'other2', ignore='/test')
        f = app.get_file('/invalid_file.sh', 'other2')
        self.assertIsNone(f)

    def test_mount_invalid_path_raises_exception(self):
        with self.assertRaises(IOError):
            app.mount('./testXXXX', 'other3', ignore='/test')
