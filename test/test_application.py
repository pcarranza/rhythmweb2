import os
import unittest

from mock import Mock
from serve.app import CGIApplication
from serve import CGIServer
from urllib.request import urlopen

from rhythmweb.conf import Configuration

class TestCGIApplication(unittest.TestCase):

    def test_build_application(self):
        app = CGIApplication('', Mock())
        self.assertIsNotNone(app)


class TestCGIServer(unittest.TestCase):

    def test_build_server(self):
        app = Mock()
        server = CGIServer(app)
        self.assertIsNotNone(server)

    def test_full_stack_handle_request(self):
        config = Configuration()
        app = CGIApplication(os.path.abspath('.'), config)
        server = CGIServer(app)
        try:
            server.start()
            index_page = urlopen('http://localhost:7001')
            self.assertIn(index_page, '<html>')
        except:
            server.stop()
