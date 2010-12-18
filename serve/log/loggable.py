import logging
import serve.log

import sys

class Loggable(object):
    '''
    Class that allows logging methods disconnecting the main class from the logger itself
    '''

    def info(self, message):
        self._print(message, logging.INFO)

    def debug(self, message):
        self._print(message, logging.DEBUG)
    
    def error(self, message):
        self._print(message, logging.ERROR)

    def critical(self, message):
        self._print(message, logging.CRITICAL)

    def warning(self, message):
        self._print(message, logging.WARNING)
    
    def _print(self, message, level):
        logname = self.__class__.__name__
        log = serve.log.get_logger(logname)
        log.log(level, message)
        
        # sys.stderr.write('STDERR - %s\n' % message)