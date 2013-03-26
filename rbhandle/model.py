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

from entry import EntryHandler


class ModelHandler(Loggable):
    
    def __init__(self, shell):
        self.shell = shell
        
        
    def loop_query_model(self, func, query_model, first=0, limit=0):
        '''
        Loops a query model object and invokes the given function for every row, can also receive a first and a limit to "page" 
        '''
        self.trace('Loop query_model...')

        if func is None:
            raise Exception('Func cannot be None')
        if query_model is None:
            raise Exception('Query Model cannot be None')
        
        
        if first != 0:
            limit = limit + first
        
        index = 0
        count = 0
        entry_handler = EntryHandler(self.shell)
        for row in query_model:
            self.trace('Reading Row...')

            if index < first:
                index += + 1
                self.trace('Skipping row ')
                continue
            
            entry = self.get_entry_from_row(row)
            entry_id = entry_handler.load_entry(entry)
            
            func(entry_id)
            count += 1
            
            index += 1
            if limit != 0 and index >= limit:
                break
        
        return count
    
    
    def get_entry_from_row(self, row):
        '''
        Returns the entry id for a given row from a query model
        '''
        if row is None:
            raise Exception('Row from query model cannot be None')
        
        return row[0]

