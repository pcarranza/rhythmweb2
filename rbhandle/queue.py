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

from serve.log.loggable import Loggable
from model import ModelHandler
import random

class QueueHandler(Loggable):
    
    def __init__(self, shell):
        self.shell = shell
    
    def get_play_queue(self, queue_limit=100):
        '''
        Returns the play queue, limited to 100 entries by default
        '''
        self.info('Getting play queue')
        entries = []
        
        m = ModelHandler(self.shell)
        m.loop_query_model(func=entries.append, query_model=self.get_play_queue_model(), limit=queue_limit)
        return entries
    
    
    def get_play_queue_model(self):
        '''
        Returns the main play queue query model
        '''
        return self.shell.props.queue_source.props.query_model
    
    
    def clear_play_queue(self):
        '''
        Cleans the playing queue
        '''
        m = ModelHandler(self.shell)
        m.loop_query_model(func=self.dequeue, query_model=self.get_play_queue_model())
    
    
    def shuffle_queue(self):
        self.debug('shuffling queue')
        entries = self.get_play_queue()
        if entries:
            self.debug('There are entries, actually shuffling the queue')
            random.shuffle(entries)
            
            for i in range(0, len(entries) - 1):
                entry = self.get_entry(entries[i])
                self.move_entry_in_queue(entry, i)
    
    
    def move_entry_in_queue(self, entry, index):
        queue = self.shell.props.queue_source
        queue.move_entry(entry, index)
    
    
    def enqueue(self, entry_ids):
        '''
        Appends the given entry id or ids to the playing queue 
        '''
        self.info('Adding entries %s to queue' % entry_ids)
        if type(entry_ids) is list:
            for entry_id in entry_ids:
                entry = self.load_rb_entry(entry_id)
                if entry is None:
                    continue
                location = str(entry.location)
                self.debug('Enqueuing entry %s' % location)
                self.shell.add_to_queue(location)
        elif type(entry_ids) is int:
            entry = self.load_rb_entry(entry_ids)
            if not entry is None:
                location = str(entry.location)
                self.debug('Enqueuing entry %s' % location)
                self.shell.add_to_queue(location)
                
        self.shell.props.queue_source.queue_draw()
        
        
    def dequeue(self, entry_ids):
        '''
        Removes the given entry id or ids from the playing queue 
        '''
        if type(entry_ids) is list:
            self.info('Removing entries %s from queue' % entry_ids)
            for entry_id in entry_ids:
                entry = self.load_rb_entry(entry_id)
                if entry is None:
                    continue
                location = str(entry.location)
                self.trace('Dequeuing entry %s' % location)
                self.shell.remove_from_queue(location)
        elif type(entry_ids) is int:
            self.info('Removing entry %d from queue' % entry_ids)
            entry = self.load_rb_entry(entry_ids)
            if not entry is None:
                location = str(entry.location)
                self.trace('Dequeuing entry %s' % location)
                self.shell.remove_from_queue(location)
                
        self.shell.props.queue_source.queue_draw()

