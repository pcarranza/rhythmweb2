from serve.rest.base import BaseRest
from serve.log.loggable import Loggable
from serve.request import ServerException


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
        
        else:
            raise ServerException(400, 'Bad request, action %s is not supported' % action)
            
        return 'OK'
    
    
    
            