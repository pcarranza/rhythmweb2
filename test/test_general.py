
import os
import unittest
from mock import patch, Mock, call

from rhythmweb.conf import Configuration


class ConfigurationTest(unittest.TestCase):

    def test_default_configuration(self):
        base_path = os.path.dirname(__file__)
        config_path = os.path.join(base_path, '..', 'cfg', 'rb-serve.conf')
        config = Configuration()
        self.assertEquals('default', config.get_string('theme'))
        self.assertEquals('touch', config.get_string('theme.mobile'))
        self.assertEquals('0.0.0.0', config.get_string('hostname'))
        self.assertEquals(7000, config.get_int('port'))
        self.assertEquals('/tmp/rb-serve.log', config.get_string('log.file'))
        self.assertEquals('%(levelname)s	%(asctime)s	%(name)s: %(message)s', config.get_string('log.format'))
        self.assertEquals('INFO', config.get_string('log.level'))
        self.assertEquals(False, config.get_boolean('debug'))

    def test_print_configuration(self):
        with patch('rhythmweb.conf.logging') as log:
            root = Mock()
            log.getLogger.return_value = root
            config = Configuration()
            config.parser.set('server', 'log.level', 'DEBUG')
            config.configure_logger()
            root.debug.assert_has_calls([
                call('Logger configured'),
                call('Showing app configuration:')])
