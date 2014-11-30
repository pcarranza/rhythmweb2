import os
import unittest

from mock import Mock, patch
from urllib.request import urlopen, HTTPError

from rhythmweb.conf import Configuration
from rhythmweb import view, controller, rb
from rhythmweb.server import Server
from utils import Stub


class TestServer(unittest.TestCase):

    def setUp(self):
        self.rb = Mock(rb.RBHandler)
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        conf = Configuration()
        conf.parser.set('server', 'port', '7003')
        self.conf_patch = patch('rhythmweb.server.Configuration')
        conf_mock = self.conf_patch.start()
        conf_mock.return_value = conf

    def tearDown(self):
        self.conf_patch.stop()

    def test_full_server_stack(self):
        server = Server()
        try:
            server.start()
            response = urlopen('http://localhost:7003')
            self.assertEquals(response.code, 200)
            html = response.read().decode('UTF-8')
            self.assertTrue('html' in html)
        finally:
            server.stop()

    def test_full_server_stack_not_found_handling(self):
        self.rb.get_entry.return_value = None
        server = Server()
        try:
            server.start()
            urlopen('http://localhost:7003/rest/song/1')
            self.assertTrue(False)
        except HTTPError as e:
            self.assertEquals(e.code, 404)
        finally:
            server.stop()

    def test_full_server_stack_error_handling(self):
        self.rb.get_entry.side_effect = RuntimeError('just because')
        server = Server()
        try:
            server.start()
            urlopen('http://localhost:7003/rest/song/1')
            self.assertTrue(False)
        except HTTPError as e:
            self.assertEquals(e.code, 500)
        finally:
            server.stop()

    def test_full_server_stack_post_handling(self):
        self.rb.get_entry.return_value = Stub(id=2)
        server = Server()
        try:
            server.start()
            response = urlopen('http://localhost:7003/rest/song/2', data=bytes('rating=5', 'UTF-8'))
            self.assertEquals(response.code, 200)
        finally:
            server.stop()
