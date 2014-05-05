import unittest

from os import path
from rhythmweb import RhythmWeb
from mock import patch, Mock


@patch('serve.log')
class TestPluginLoading(unittest.TestCase):

    def test_creating_the_plugin_works(self, logger):
        logger.get_factory = Mock()
        rw = RhythmWeb()
        self.assertIsNotNone(rw)
        self.assertEquals(path.abspath(path.join(
            path.dirname(__file__), '..')), rw.base_path)
        self.assertIsNotNone(rw.config)

    @patch('rhythmweb.CGIApplication')
    @patch('rhythmweb.CGIServer')
    def test_activation_creates_cgi_app(self, server_class, app_patch, logger):
        rb = RhythmWeb()
        rb.config = Mock()
        server = Mock()
        server_class.return_value = server
        rb.do_activate()
        self.assertEquals(rb.object.server, server)
        server.start.assert_called_once_with()
        rb.do_deactivate()
        server.stop.assert_called_once_with()

    def test_deactivation_without_previous_activation(self, logger):
        rb = RhythmWeb()
        rb.do_deactivate()


