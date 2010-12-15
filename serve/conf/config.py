import os, sys

class Configuration:
    
    _instance = None
    
    @staticmethod
    def get_instance():
        if Configuration._instance is None:
            Configuration._instance = Configuration()
            
        return Configuration._instance
    
    
    _params = None
    
    def __init__(self):
        self._params = {}
        self.debug('New configuration instance')
        
        
    def debug(self, message):
        sys.stderr.write('%s\n' % message)
        
    
    def load_configuration(self, path):
        
        if not os.path.exists(path):
            self.debug('Path %s does not exists' % path)
            raise ConfigurationFileDoesNotExistsException(path)
        
        file = open(path, 'r')
        
        if not file:
            raise Exception()
        
        for line in file:
            line = str(line).strip()
            
            if not line:
                continue
            
            if line.startswith('#'):
                continue
            
            self._readConfigurationLine(line)
        
        
    def _readConfigurationLine(self, line):
        (key, value) = line.split('=')
        if not key:
            self.debug('Line \"%s\" has no key' % line)
            raise InvalidConfigurationLineException(line)
        key = str(key).strip()
        
        if not value:
            self.debug('Key \"%s\" has no value' % key)
            value = ''
            
        value = str(value).strip()
        
        self.debug('Setting value \"%s\" for key \"%s\"' % (value, key))
        self._params[key] = value
        
        
    def _getParameter(self, key, required, defaultValue):
        if not self._params.has_key(key):
            if required:
                raise RequiredParameterException(key)
            else:
                return defaultValue
            
        return self._params[key]
    
        
    def getBoolean(self, key, required=False, defaultValue=False):
        value = self._getParameter(key, required, defaultValue)
        if value is None:
            return False
        
        return bool(value)
    
    
    def getString(self, key, required=False, defaultValue=''):
        value = self._getParameter(key, required, defaultValue)
        if value is None:
            return ''
        
        return str(value)
    
    
    def getInt(self, key, required=False, defaultValue=0):
        value = self._getParameter(key, required, defaultValue)
        if value is None:
            return 0
        
        return int(value)
    
    
    def printConfiguration(self, logger):
        logger.info('--------------------------')
        logger.info('Showing app configuration:')
        logger.info('--------------------------')
        for key in self._params:
            logger.info('%s = %s' % (key, self._params[key]))
        logger.info('--------------------------')
        
        
# /Configuration

class CantOpenConfigurationFileException(Exception):
    
    def __init__(self):
        Exception.__init__(self)
        
# /CantOpenConfigurationFileException
        

class ConfigurationFileDoesNotExistsException(Exception):
    
    path = None
    
    def __init__(self, path):
        Exception.__init__(self, path)
        self.path = path
        
# /ConfigurationFileDoesNotExistsException

class InvalidConfigurationLineException(Exception):
    
    _line = None
    
    def __init__(self, line):
        Exception.__init__(self, line)
        self._line = line
        
# /InvalidConfigurationLineException


class RequiredParameterException(Exception):
    
    _parameter = None
    
    def __init__(self, parameter):
        Exception.__init__(self, parameter)
        self._parameter = parameter
        
# /RequiredParameterException
