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

log = logging.getLogger(__name__)

class Loggable(object):
    
    def info(self, message):
        log.info(message)

    def trace(self, message):
        log.debug(message)
    
    def debug(self, message):
        log.debug(message)
    
    def error(self, message):
        log.error(message)
    
    def critical(self, message):
        log.error(message)
    
    def warn(self, message):
        log.warn(message)
    
    def warning(self, message):
        log.warn(message)
