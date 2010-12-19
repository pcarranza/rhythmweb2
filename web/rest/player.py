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
            
            entry_ids = self.pack_as_list(params['entry_id'])
            handler.enqueue(entry_ids)
            
        elif action == 'dequeue':
            if not 'entry_id' in params:
                raise ServerException(400, 'Bad request, no entry_id parameter')
            
            entry_ids = self.pack_as_list(params['entry_id'])
            handler.dequeue(entry_ids)
        
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
    
    def unpack_value(self, value):
        if type(value) is dict:
            svalue = ''.join(value)
            self.debug('Value \"%s\" was packed as dictionary' % svalue)
        elif type(value) is list:
            if len(value) == 1:
                self.debug('Value \"%s\" was packed as 1 element list' % value[0])
                return value[0]
            
            svalue = ''.join(value)
            self.debug('Value \"%s\" was packed as list' % svalue)
        else:
            svalue = str(value)
            self.debug('Value \"%s\" was packed as plain string' % svalue)
            
        return svalue.strip()
    
    
    def pack_as_list(self, value):
        if type(value) is list:
            return value
        elif type(value) is dict:
            return_value = []
            for v in value:
                return_value.append(value[v])
            return return_value
        else:
            return [value]
            