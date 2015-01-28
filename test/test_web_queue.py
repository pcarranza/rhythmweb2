import unittest
import json

from mock import Mock, patch
from rhythmweb import view, controller, rb
from rhythmweb.server import Server
from utils import Stub, environ, handle_request

class TestWebQueue(unittest.TestCase):

    def setUp(self):
        self.rb = Mock(spec=rb.RBHandler)
        controller.rb_handler['rb'] = self.rb
        self.response = Mock()
        self.app = Server()

        self.queue_patch = patch('rhythmweb.controller.rb.Queue', spec=rb.Queue)
        self.queue_class = self.queue_patch.start()
        self.queue = Mock(spec=rb.Queue)
        self.queue_class.return_value = self.queue

    def tearDown(self):
        self.queue_patch.stop()

    def test_basic_do_get(self):
        self.queue.get_play_queue.return_value = [Stub(id=1), Stub(id=2), Stub(id=3)]
        result = handle_request(self.app, environ('/rest/queue'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.queue.get_play_queue.assert_called_with()
        for index, entry in enumerate(returned['entries'], 1):
            self.assertEquals(index, entry['id'])

    def test_basic_do_post(self):
        result = handle_request(self.app, environ('/rest/queue', post_data='bla=1'), self.response)
        self.response.assert_called_with('405 method POST not allowed',
                [('Content-type', 'text/html; charset=UTF-8')])
