import os
import unittest

from mock import Mock
from serve import CGIServer
from urllib.request import urlopen, HTTPError

from rhythmweb.conf import Configuration
from rhythmweb import view, controller
from rhythmweb.server import Server
from utils import Stub


class TestServer(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = Server()
        self.app.config = Configuration()

    def test_build_server(self):
        server = CGIServer(self.app)
        self.assertIsNotNone(server)

    def test_full_server_stack(self):
        server = CGIServer(self.app)
        try:
            server.start()
            response = urlopen('http://localhost:7000')
            self.assertEquals(response.code, 200)
            html = response.read().decode('UTF-8')
            self.assertTrue('html' in html)
        finally:
            server.stop()

    def test_full_server_stack_not_found_handling(self):
        self.rb.get_entry.return_value = None
        server = CGIServer(self.app)
        try:
            server.start()
            urlopen('http://localhost:7000/rest/song/1')
            self.assertTrue(False)
        except HTTPError as e:
            self.assertEquals(e.code, 404)
        finally:
            server.stop()

    def test_full_server_stack_error_handling(self):
        self.rb.get_entry.side_effect = RuntimeError('just because')
        server = CGIServer(self.app)
        try:
            server.start()
            urlopen('http://localhost:7000/rest/song/1')
            self.assertTrue(False)
        except HTTPError as e:
            self.assertEquals(e.code, 500)
        finally:
            server.stop()

    def test_full_server_stack_post_handling(self):
        self.rb.load_entry.return_value = Stub(2)
        server = CGIServer(self.app)
        try:
            server.start()
            response = urlopen('http://localhost:7000/rest/song/2', data=bytes('rating=5', 'UTF-8'))
            self.assertEquals(response.code, 200)
        finally:
            server.stop()
