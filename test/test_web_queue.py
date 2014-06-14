import unittest
import json

from mock import Mock
from rhythmweb import controller
from utils import Stub, cgi_application, environ, handle_request

class TestWebQueue(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.response = Mock()
        self.app = cgi_application()

    def test_basic_do_get(self):
        self.rb.get_play_queue.return_value = [Stub(1), Stub(2), Stub(3)]
        result = handle_request(self.app, environ('/rest/queue'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.rb.get_play_queue.assert_called_with()
        for index, entry in enumerate(returned['entries'], 1):
            self.assertEquals(index, entry['id'])

    def test_basic_do_post(self):
        result = handle_request(self.app, environ('/rest/queue', post_data='bla=1'), self.response)
        self.response.assert_called_with('405 method POST not allowed',
                [('Content-type', 'text/html; charset=UTF-8')])
