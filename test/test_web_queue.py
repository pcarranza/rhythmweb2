
import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.queue import Page
from utils import Stub

class TestWebQueue(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_basic_do_get(self):
        page = Page(self.components)
        environ = defaultdict(lambda: '')
        response = Mock()
        self.rb.get_play_queue.return_value = [Stub(1), Stub(2), Stub(3)]
        result = page.do_get(environ, response)
        response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.rb.get_play_queue.assert_called_with()
        for index, entry in enumerate(returned['entries'], 1):
            self.assertEquals(index, entry['id'])

    def test_basic_do_post(self):
        page = Page(self.components)
        environ = defaultdict(lambda: '')
        params = defaultdict(lambda: '')
        response = Mock()
        result = page.do_post(environ, params, response)
        response.assert_called_with('405 method POST not allowed',
                [('Content-type', 'text/html; charset=UTF-8')])

