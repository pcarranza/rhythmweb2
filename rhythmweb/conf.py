from os import path
from configparser import SafeConfigParser

import logging

log = logging.getLogger(__name__)

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
            'log.level' : 'DEBUG',
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

    def print_configuration(self):
        log.info('Showing app configuration:')
        for section_name in self.parser.sections():
            log.info('Section: %s' % section_name)
            for key in self.parser.options(section_name):
                log.info('  %s = %s' % (key, self.parser.get(section_name, key, raw=True)))
