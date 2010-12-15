
import logging

class LoggerFactory:

    _instance = None
    
    @staticmethod
    def get_factory():
        if LoggerFactory._instance is None:
            LoggerFactory._instance = LoggerFactory()
            
        return LoggerFactory._instance


    def __init__(self):
        self._loggers = {}
        
    
    def configure(self, config):
        self._loggers.clear()
        
        logfilename = config.getString('log.file', 
                                         False, 
                                         'web.log')
        default_log_level = config.getInt('log.level', \
                                        False, \
                                        logging.INFO)
        log_format = config.getString('log.format', \
                                      False, \
                                      logging.BASIC_FORMAT)
        
        logging.basicConfig(filename=logfilename, \
                            level=default_log_level, \
                            format=log_format)
        
        logging.info('Logger factory started with file %s and level %s' % 
                     (logfilename, 
                     logging.getLevelName(default_log_level)))    
        logging.debug('ROOT LOGGER LEVEL: %s' % logging.getLevelName(logging.root.level))
        

    def getLogger(self, name):
        
        if self._loggers.has_key(name):
            return self._loggers[name]
        
        log = logging.getLogger(name)
        log.setLevel(logging.root.level)

        logging.debug('Created logger %s with level %s' % (
                   name,
                   logging.getLevelName(log.level)))
        
        self._loggers[name] = log

        return log
    
