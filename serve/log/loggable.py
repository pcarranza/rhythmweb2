'''
Created on 31/10/2010

@author: jim
'''
from serve.log.factory import LoggerFactory
from serve.conf.config import Configuration
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
        loggerclazz = self.__class__
        logname = loggerclazz.__name__
        if Configuration.instance().getBoolean('debug'):
            print '%s - %s' % (logname, message)
            
        log = LoggerFactory.getLogger(loggerclazz)
        log.log(level, message)
