from os import path
from configparser import SafeConfigParser

import logging
import logging.handlers

class Configuration(object):

    def __init__(self):
        self.parser = SafeConfigParser(defaults={
            'theme' : 'default',
            'theme.mobile' : 'touch',
            'hostname' : '127.0.0.1',
            'port' : '7001',
            'proxy' : 'True',
            'proxy.hostname' : '0.0.0.0',
            'proxy.port' : '7000',
            'log.file' : '/tmp/rb-serve.log',
            'log.level' : 'INFO',
            'log.format' : '%(levelname)s	%(asctime)s	%(name)s: %(message)s',
            'debug' : 'False',
            })
        self.parser.add_section('server')
        self.parser.read(path.expanduser('~/.rhythmweb'))

    def get_string(self, key):
        return self.parser.get('server', key, raw=True)

    def get_int(self, key):
        return self.parser.getint('server', key)

    def get_boolean(self, key):
        return self.parser.getboolean('server', key)

    def configure_logger(self):
        root = logging.getLogger()
        root.setLevel(self.get_string('log.level'))
        handler = logging.handlers.RotatingFileHandler(
                self.get_string('log.file'),
                backupCount=5, 
                maxBytes=1024*1024)
        handler.setFormatter(logging.Formatter(fmt=self.get_string('log.format')))
        root.addHandler(handler)

        if root.isEnabledFor(logging.DEBUG):
            root.debug('Logger configured')
            root.debug('Showing app configuration:')
            for section_name in self.parser.sections():
                root.debug('Section: %s' % section_name)
                for key in self.parser.options(section_name):
                    root.debug('  %s = %s' % (key, self.parser.get(section_name, key, raw=True)))

