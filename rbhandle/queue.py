from .model import ModelHandler
import random

import logging
log = logging.getLogger(__name__)

class QueueHandler(object):
    
    def __init__(self, shell):
        self.shell = shell
    
    def get_play_queue(self, queue_limit=100):
        '''
        Returns the play queue, limited to 100 entries by default
        '''
        log.info('Getting play queue')
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
        log.debug('shuffling queue')
        entries = self.get_play_queue()
        if entries:
            log.debug('There are entries, actually shuffling the queue')
            random.shuffle(entries)
            
            for i in range(0, len(entries) - 1):
                entry = self.shell.props.db.entry_lookup_by_id(int(entries[i].id))
                self.move_entry_in_queue(entry, i)
    
    def move_entry_in_queue(self, entry, index):
        queue = self.shell.props.queue_source
        queue.move_entry(entry, index)
    
    def enqueue(self, entry_ids):
        '''
        Appends the given entry id or ids to the playing queue 
        '''
        log.info('Adding entries %s to queue' % entry_ids)
        if type(entry_ids) is list:
            for entry_id in entry_ids:
                entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
                if entry is None:
                    continue
                self.shell.props.queue_source.add_entry(entry, -1)

        elif type(entry_ids) is int:
            entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
            if not entry is None:
                self.shell.props.queue_source.add_entry(entry, -1)
        else:
            log.info('Plain RBEntry')
            entry = self.shell.props.db.entry_lookup_by_id(entry_ids.id)
            self.shell.props.queue_source.add_entry(entry, -1)

        self.shell.props.queue_source.queue_draw()
        
        
    def dequeue(self, entry_ids):
        '''
        Removes the given entry id or ids from the playing queue 
        '''
        if type(entry_ids) is list:
            log.info('Removing entries %s from queue' % entry_ids)
            for entry_id in entry_ids:
                entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
                if entry is None:
                    continue
                self.shell.props.queue_source.remove_entry(entry)
        elif type(entry_ids) is int:
            log.info('Removing entry %d from queue' % entry_ids)
            entry = self.shell.props.db.entry_lookup_by_id(int(entry_id))
            if not entry is None:
                location = str(entry.location)
                self.shell.props.queue_source.remove_entry(entry)
                
        self.shell.props.queue_source.queue_draw()
