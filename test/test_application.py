import os
import unittest

from mock import Mock
from serve.app import CGIApplication
from serve import CGIServer
from urllib.request import urlopen, HTTPError

from rhythmweb.conf import Configuration
from rhythmweb import controller
from utils import Stub

class TestCGIApplication(unittest.TestCase):

    def test_build_application(self):
        app = CGIApplication('', Mock())
        self.assertIsNotNone(app)


class TestCGIServer(unittest.TestCase):

    def test_build_server(self):
        app = Mock()
        server = CGIServer(app)
        self.assertIsNotNone(server)

    def test_full_server_stack(self):
        config = Configuration()
        app = CGIApplication(os.path.abspath('.'), config)
        server = CGIServer(app)
        try:
            server.start()
            response = urlopen('http://localhost:7000')
            self.assertEquals(response.code, 200)
            html = response.read().decode('UTF-8')
            self.assertTrue('html' in html)
        finally:
            server.stop()

    def test_full_server_stack_not_found_handling(self):
        rb = Mock()
        rb.get_entry.return_value = None
        controller.rb_handler['rb'] = rb
        config = Configuration()
        app = CGIApplication(os.path.abspath('.'), config)
        server = CGIServer(app)
        try:
            server.start()
            urlopen('http://localhost:7000/rest/song/1')
            self.assertTrue(False)
        except HTTPError as e:
            self.assertEquals(e.code, 404)
        finally:
            server.stop()

    def test_full_server_stack_error_handling(self):
        rb = Mock()
        rb.get_entry.side_effect = ValueError('just because')
        controller.rb_handler['rb'] = rb
        config = Configuration()
        app = CGIApplication(os.path.abspath('.'), config)
        server = CGIServer(app)
        try:
            server.start()
            urlopen('http://localhost:7000/rest/song/1')
            self.assertTrue(False)
        except HTTPError as e:
            self.assertEquals(e.code, 500)
        finally:
            server.stop()

    def test_full_server_stack_post_handling(self):
        rb = Mock()
        rb.load_entry.return_value = Stub(2)
        controller.rb_handler['rb'] = rb
        config = Configuration()
        app = CGIApplication(os.path.abspath('.'), config)
        server = CGIServer(app)
        try:
            server.start()
            response = urlopen('http://localhost:7000/rest/song/2', data=bytes('rating=5', 'UTF-8'))
            self.assertEquals(response.code, 200)
        finally:
            server.stop()
