
import logging
import sys
from serve.conf.config import Configuration


class LoggerFactory():
    
    _instance = None
    _default_log_level = None

    @staticmethod
    def getFactory():
        if LoggerFactory._instance is None:
            sys.stdout.write('Creating new logger factory')
            LoggerFactory._instance = LoggerFactory()
        return LoggerFactory._instance
    
    
    @staticmethod
    def getLogger(clazz):
        factory = LoggerFactory.getFactory()
        return factory._getLogger(clazz.__name__)

    _name = 'LoggerFactory'
    _loggers = {}
    # TODO: load from configuration
    
    def __init__(self):
        logfilemane = Configuration.instance().getString('log.file', 
                                                         False, 
                                                         'rhythmweb.log')
        LoggerFactory._default_log_level = Configuration.instance().getInt(\
                                            'log.level', \
                                            False, \
                                            logging.INFO)
        
        logging.basicConfig(filename=logfilemane, level=LoggerFactory._default_log_level)
        log = self._getLogger(self._name)
        self._loggers[self._name] = log
        
    
    def _getLogger(self, name):
        if self._loggers.has_key(name):
            return self._loggers[name]
        
        loglevel = Configuration.instance().getString('log.level.%s' % name, \
                                                      False, \
                                                      LoggerFactory._default_log_level)
        
        log = logging.getLogger(name)
        self.configureLogger(log, loglevel)
        self._loggers[name] = log
        
        return log
    
    
    def configureLogger(self, log, level):
        log.setLevel(level)
    
        
    def __getattr__(self, aAttr):
        return getattr(self._instance, aAttr)        
    
    
    def __setattr__(self, aAttr, aValue):
        return setattr(self._instance, aAttr, aValue)    
