# Rhythmweb - Rhythmbox web REST + Ajax environment for remote control
# Copyright (C) 2010  Pablo Carranza
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys

class Configuration:
    
    _params = None
    
    def __init__(self):
        self._params = {}
        self.__config_log = []
        self.__config_log.append(' - New configuration instance')
        
        
    def debug(self, message):
        sys.stderr.write('%s\n' % message)
        
    
    def load_configuration(self, path):
        
        if not os.path.exists(path):
            sys.stderr.write('Configuration path %s does not exists\n' % path)
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
            self.__config_log.append('Line \"%s\" has no key' % line)
            raise InvalidConfigurationLineException(line)
        key = str(key).strip()
        
        if not value:
            self.__config_log.append('Key \"%s\" has no value' % key)
            value = ''
            
        value = str(value).strip()
        
        self.__config_log.append('Setting value \"%s\" for key \"%s\"' % (value, key))
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
        if self.getBoolean('debug', False, False):
            logger.info('Configuration process:')
            for line in self.__config_log:
                logger.info(line)
            
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
