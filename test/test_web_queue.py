
import unittest
import json

from rhythmweb import controller
from collections import defaultdict
from mock import Mock
from web.rest.queue import Page
from utils import Stub

class TestWebQueue(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.response = Mock()
        self.environ = defaultdict(lambda: '')
        self.params = defaultdict(lambda: '')

    def test_build(self):
        page = Page()
        self.assertIsNotNone(page)

    def test_basic_do_get(self):
        page = Page()
        self.rb.get_play_queue.return_value = [Stub(1), Stub(2), Stub(3)]
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.rb.get_play_queue.assert_called_with()
        for index, entry in enumerate(returned['entries'], 1):
            self.assertEquals(index, entry['id'])

    def test_basic_do_post(self):
        page = Page()
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('405 method POST not allowed',
                [('Content-type', 'text/html; charset=UTF-8')])

