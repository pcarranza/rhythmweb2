# -*- coding: utf-8 -
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
import serve.log
import sys
from serve.log import LEVEL_TRACE


class Loggable(object):
    
    factory = None
    
    def get_logger_factory(self):
        if Loggable.factory is None:
            Loggable.factory = serve.log.get_factory()
            
        return Loggable.factory
    
    
    def info(self, message):
        self.__print(message, logging.INFO)


    def trace(self, message):
        self.__print(message, LEVEL_TRACE)
    
    
    def debug(self, message):
        self.__print(message, logging.DEBUG)
    
    
    def error(self, message):
        self.__print(message, logging.ERROR)
        
    
    def critical(self, message):
        self.__print(message, logging.CRITICAL)
        
    
    def warn(self, message):
        self.warning(message)
    
    
    def warning(self, message):
        self.__print(message, logging.WARNING)
        
    
    def __print(self, message, level):
        log = self.get_logger_factory().get_logger(self.get_logname())
        log.log(level, message)
        if level >= log.level:
            print >> sys.stdout, message
        
        
    def get_logname(self):
        return self.__class__.__name__
