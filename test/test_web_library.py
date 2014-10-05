import unittest
import json

from mock import Mock
from rhythmweb import view, controller
from rhythmweb.server import Server
from utils import Stub, environ, handle_request

class TestWebLibrary(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = Server()

    def test_get_without_parameters_fails(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/library'), self.response)
        self.response.assert_called_with('404 NOT FOUND',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_basic_do_get(self):
        self.rb.library.artists = {'values' : {'a guy' : 55}, 'max': 55}
        result = handle_request(self.app, environ('/rest/library/artists'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{"values": {"a guy": 55}, "max": 55}')
        returned = json.loads(result)
        self.assertEquals(expected, returned)

    def test_invalid_search_type_fails(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/library/calabaza'), self.response)
        self.response.assert_called_with('400 Bad Request: Invalid library filter "calabaza"',
                [('Content-type', 'text/html; charset=UTF-8')])
