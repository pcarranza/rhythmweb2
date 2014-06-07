import logging

from web.rest import RBRest
from serve.request import ClientError
from rhythmweb.controller import Queue, Player


log = logging.getLogger(__name__)

class Page(RBRest):
    
    def post(self):
        if not self.has_post_parameters():
            raise ClientError('no parameters')
        rb = self.get_rb_handler()
        action = self.get_parameter('action', True)
        player = Player(rb)
        log.info('POST action %s' % action)
        if action in ('play_pause', 'next', 'previous', 'seek', 'play_entry', 
                      'mute', 'set_volume'):
            method = getattr(player, action)
            method(**self.get_args())
        elif action in ('enqueue', 'dequeue', 'shuffle_queue', 'clear_queue'):
            queue = Queue(rb)
            method = getattr(queue, action)
            method(**self.get_args())
        else:
            raise ClientError('action "%s" is not supported' % action)
        status = player.status()
        status['last_action'] = action
        return status

    def get_args(self):
        kwargs = {}
        if 'time' in self.post_parameters:
            time = self.get_int_parameter('time')
            if not time:
                raise ClientError('time parameter must be an integer number')
            kwargs['time'] = time

        if 'entry_id' in self.post_parameters:
            kwargs['entry_id'] = self.get_parameter('entry_id', True)

        if 'volume' in self.post_parameters:
            try:
                volume = float(self.get_parameter('volume', True))
            except:
                raise ClientError('volume parameter must be float type')
            kwargs['volume'] = volume
        return kwargs
