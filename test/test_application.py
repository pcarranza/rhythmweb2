import os
import unittest

from mock import Mock
from serve.app import CGIApplication
from serve import CGIServer


class TestCGIApplication(unittest.TestCase):

    def test_build_application(self):
        app = CGIApplication('', Mock())
        self.assertIsNotNone(app)


class TestCGIServer(unittest.TestCase):

    def test_build_server(self):
        app = Mock()
        server = CGIServer(app)
        self.assertIsNotNone(server)
