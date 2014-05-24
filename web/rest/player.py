import logging

from web.rest import RBRest
from serve.request import ServerException
from rhythmweb.model import get_status

log = logging.getLogger(__name__)

class Page(RBRest):
    
    def post(self):
        if not self.has_post_parameters():
            raise ServerException(400, 'Bad request, no parameters')
        action = self.get_parameter('action', True)
        handler = self.get_rb_handler()
        log.info('POST action %s' % action)
        if action == 'play_pause':
            handler.play_pause()
        elif action == 'next':
            handler.play_next()
        elif action == 'previous':
            handler.previous()
        elif action == 'seek':
            time = self.get_int_parameter('time')
            if not time:
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
        status = get_status(handler)
        status['last_action'] = action
        return status
