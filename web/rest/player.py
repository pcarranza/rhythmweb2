import logging

from web.rest import RBRest
from serve.app import ClientError
from rhythmweb.controller import Queue, Player


log = logging.getLogger(__name__)

class Page(RBRest):

    def post(self):
        action = self.get_parameter('action', True)
        player = Player()
        log.info('POST action %s' % action)
        if action in ('play_pause', 'next', 'previous', 'seek', 'play_entry',
                      'mute', 'set_volume'):
            method = getattr(player, action)
            method(**self.get_args())
        elif action in ('enqueue', 'dequeue', 'shuffle_queue', 'clear_queue'):
            queue = Queue()
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
            kwargs['time'] = self.to_int(self.get_parameter('time', True),
                    'time must be a number')

        if 'entry_id' in self.post_parameters:
            entry_id = self.get_parameter('entry_id', True)
            if ',' in entry_id:
                entries = [int(entry) for entry in entry_id.split(',')]
            else:
                entries = int(entry_id)
            kwargs['entry_id'] = entries

        if 'volume' in self.post_parameters:
            kwargs['volume'] = self.to_float(self.get_parameter('volume', True),
                'volume must be number')

        return kwargs
