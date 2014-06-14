import unittest
import json

from mock import Mock
from rhythmweb import controller
from utils import Stub, cgi_application, environ, handle_request

class TestWebStatus(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = cgi_application()

    def test_load_index(self):
        result = handle_request(self.app, environ(''), self.response)
        self.assertIn('<html>', result)

    def test_not_found(self):
        result = handle_request(self.app, environ('invalid_file'), self.response)
        self.assertEquals('ERROR: Could not find resource /invalid_file', result)
        self.response.assert_called_with('404 Could not find resource /invalid_file', 
                [('Content-type', 'text/html; charset=UTF-8')])
