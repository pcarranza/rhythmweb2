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

import logging


class LoggerFactory:

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

    
_factory = LoggerFactory()


def get_factory():
    return _factory


def get_logger(name):
    return get_factory().getLogger(name)
