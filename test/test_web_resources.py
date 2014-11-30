import unittest
import json

from mock import Mock
from rhythmweb import view, controller, rb
from rhythmweb.server import Server
from utils import Stub, environ, handle_request

class TestWebStatus(unittest.TestCase):

    def setUp(self):
        self.rb = Mock(rb.RBHandler)
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = Server()

    def test_load_index(self):
        result = handle_request(self.app, environ('/'), self.response)
        self.assertIn('<html>', result)

    def test_load_index_by_full_name(self):
        result = handle_request(self.app, environ('/index.html'), self.response)
        self.assertIn('<html>', result)

    def test_load_style(self):
        result = handle_request(self.app, environ('/style.css'), self.response)
        self.assertIsNotNone(result)

    def test_load_image(self):
        result = self.app.handle_request(environ('/img/star.png'), self.response)
        self.assertIsNotNone(result)

    def test_not_found(self):
        result = handle_request(self.app, environ('invalid_file'), self.response)
        self.response.assert_called_with('404 NOT FOUND', 
                [('Content-type', 'text/html; charset=UTF-8')])
