import unittest

from os import path
from rhythmweb import RhythmWeb
from mock import patch, Mock, call


class TestPluginLoading(unittest.TestCase):

    def test_creating_the_plugin_works(self):
        rw = RhythmWeb()
        self.assertIsNotNone(rw)
        self.assertIsNotNone(rw.config)

    @patch('rhythmweb.CGIServer')
    @patch('rhythmweb.logging')
    def test_activation_creates_cgi_app(self, logging, server_class):
        log = Mock()
        logging.getLogger.return_value = log
        rb = RhythmWeb()
        rb.config = Mock()
        server = Mock()
        server_class.return_value = server
        rb.do_activate()
        self.assertEquals(rb.object.server, server)
        server.start.assert_called_once_with()
        rb.do_deactivate()
        server.stop.assert_called_once_with()
        log.info.assert_called([call('RhythmWeb server stopped'),
            call('RhythmWeb server started'), call('RhythmWeb plugin created')])

    def test_deactivation_without_previous_activation(self):
        rb = RhythmWeb()
        rb.do_deactivate()


