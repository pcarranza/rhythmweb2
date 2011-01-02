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

from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from serve.request import ServerException
from web.rest import Status


class Page(BaseRest, Loggable):
    
    
    def post(self):
        params = self._parameters
        
        if not params:
            raise ServerException(400, 'Bad request, no parameters')
        
        if not 'action' in params:
            raise ServerException(400, 'Bad request, no action parameter')
        
        handler = self._components['RB']
        action = self.unpack_value(params['action'])
        
        self.debug('POST action %s' % action)
        if action == 'play_pause':
            handler.play_pause()
            
        elif action == 'next':
            handler.next()
            
        elif action == 'previous':
            handler.previous()
            
        elif action == 'seek':
            if not 'time' in params:
                raise ServerException(400, 'Bad request, no time parameter')
            
            time = self.unpack_value(params['time'])
            try:
                time = int(time)
            except:
                raise ServerException(400, 'Bad request, time parameter must be an integer number')
            handler.seek(time)
            
        elif action == 'enqueue':
            if not 'entry_id' in params:
                raise ServerException(400, 'Bad request, no entry_id parameter')
            self.debug('Enqueue Entry id %s' % params['entry_id'][0])
            entry_ids = self.pack_as_list(params['entry_id'][0])
            handler.enqueue(entry_ids)
            
        elif action == 'dequeue':
            if not 'entry_id' in params:
                raise ServerException(400, 'Bad request, no entry_id parameter')
            
            entry_ids = self.pack_as_list(params['entry_id'][0])
            handler.dequeue(entry_ids)
            
        elif action == 'clear_queue':
            handler.clear_play_queue()
        
        elif action == 'play_entry':
            if not 'entry_id' in params:
                raise ServerException(400, 'Bad request, no entry_id parameter')

            entry_id = self.unpack_value(params['entry_id'])
            if type(entry_id) is list:
                raise ServerException(400, 'Bad request, only one entry_id parameter accepted')
            handler.play_entry(entry_id)
            
        elif action == 'mute':
            handler.toggle_mute()
            
        elif action == 'set_volume':
            if not 'volume' in params:
                raise ServerException(400, 'Bad request, no volume parameter')
            
            volume = self.unpack_value(params['volume'])
            try:
                volume = float(volume)
            except:
                raise ServerException(400, 'Bad request, volume parameter must be float type')
            handler.set_volume(volume)
            
        else:
            raise ServerException(400, 'Bad request, action %s is not supported' % action)
            
        status = Status.get_status_as_JSon(handler)
        status.put('last_action', action)
        
        return status
    
    
    
            