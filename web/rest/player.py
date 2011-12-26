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


from web.rest import RBRest
from serve.request import ServerException


class Page(RBRest):
    
    def post(self):
        if not self.has_post_parameters():
            raise ServerException(400, 'Bad request, no parameters')
        
        action = self.get_parameter('action', True)
        handler = self.get_rb_handler()
        
        self.info('POST action %s' % action)
        
        if action == 'play_pause':
            handler.play_pause()
            
            
        elif action == 'next':
            handler.next()
            
            
        elif action == 'previous':
            handler.previous()
            
            
        elif action == 'seek':
            time = self.get_parameter('time', True)
            
            try:
                time = int(time)
            except:
                raise ServerException(400, 'Bad request, time parameter must be an integer number')
            
            handler.seek(time)
            
            
        elif action == 'enqueue':
            entry_id = self.get_parameter('entry_id', True)
            entry_ids = self.pack_as_list(entry_id)
            handler.enqueue(entry_ids)
            
            
        elif action == 'dequeue':
            entry_id = self.get_parameter('entry_id', True)
            entry_ids = self.pack_as_list(entry_id)
            handler.dequeue(entry_ids)
            
            
        elif action == 'shuffle_queue':
            handler.shuffle_queue()
            
            
        elif action == 'clear_queue':
            handler.clear_play_queue()
        
        
        elif action == 'play_entry':
            entry_id = self.get_parameter('entry_id', True)
            if type(entry_id) is list:
                raise ServerException(400, 'Bad request, only one entry_id parameter accepted')
            handler.play_entry(entry_id)
        
        
        elif action == 'mute':
            handler.toggle_mute()
        
            
        elif action == 'set_volume':
            volume = self.get_parameter('volume', True)
            try:
                volume = float(volume)
            except:
                raise ServerException(400, 'Bad request, volume parameter must be float type')
            
            handler.set_volume(volume)
            
            
        else:
            raise ServerException(400, 'Bad request, action "%s" is not supported' % action)
            

        status = self.get_status_as_json()        
        status.put('last_action', action)
        
        return status
    
    
    def get_logname(self):
        return 'PLAYER'
