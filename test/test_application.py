import os
import unittest

from mock import Mock
from serve.app import CGIApplication
from serve import CGIServer

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestCGIApplication(unittest.TestCase):

    def test_build_application(self):
        app = CGIApplication(base_path, Mock())
        self.assertIsNotNone(app)


class TestCGIServer(unittest.TestCase):

    def test_build_server(self):
        app = Mock()
        server = CGIServer(app)
        self.assertIsNotNone(server)
