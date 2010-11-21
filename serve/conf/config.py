import os

class Configuration:
    
    _instance = None
    
    _params = {}
    _path = None
    
    @staticmethod
    def instance(path=None):
        if Configuration._instance is None:
            Configuration._instance = Configuration()
        
        if not path is None:
            Configuration._instance.load_configuration(path)
        
        return Configuration._instance
    
    
    def load_configuration(self, path=None):
        if not path:
            pass
        else:
            self._path = path
        
        if not os.path.exists(self._path):
            raise ConfigurationFileDoesNotExistsException(path)
        
        file = open(self._path, 'r')
        
        if not file:
            raise Exception()
        
        self._params = {}
        
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
            raise InvalidConfigurationLineException(line)
        key = str(key).strip()
        
        if not value:
            value = ''
        value = str(value).strip()
        
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
    
    
    def printConfiguration(self):
        print '--------------------------'
        print 'Showing app configuration:'
        print '--------------------------'
        for key in self._params:
            print ('%s=%s' % (key, self._params[key]))
        print '--------------------------'
            
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
