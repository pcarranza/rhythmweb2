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

class Loggable(object):

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
        logname = self.get_logname()
        log = serve.log.get_logger(logname)
        log.log(level, message)
        
        # sys.stderr.write('STDERR - %s\n' % message)
    
    def get_logname(self):
        return self.__class__.__name__