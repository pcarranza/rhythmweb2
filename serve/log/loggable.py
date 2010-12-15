'''
Created on 31/10/2010

@author: jim
'''
from serve.log.factory import LoggerFactory
import logging

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
        factory = LoggerFactory.get_factory()
        logname = self.__class__.__name__
        log = factory.getLogger(logname)
        log.log(level, message)
