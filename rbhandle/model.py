from .entry import EntryHandler

import logging
log = logging.getLogger(__name__)


class ModelHandler(object):
    
    def __init__(self, shell):
        self.shell = shell
        
    def loop_query_model(self, func, query_model, first=0, limit=0):
        '''
        Loops a query model object and invokes the given function for every row, can also receive a first and a limit to "page" 
        '''
        log.debug('Loop query_model...')

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
            log.debug('Reading Row...')

            if index < first:
                index += + 1
                log.debug('Skipping row ')
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
