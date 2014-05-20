import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.status import Page
from utils import Stub

class TestWebStatus(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_get_status(self):
        try:
            page = Page(self.components)
            entry = Stub()
            response = Mock()
            environ = defaultdict(lambda: '')
            self.rb.get_playing_status.return_value = False
            self.rb.get_play_order.return_value = 'bla'
            self.rb.get_mute.return_value = True
            self.rb.get_volume.return_value = 1
            result = page.do_get(environ, response)
            response.assert_called_with('200 OK', 
                    [('Content-type', 'application/json; charset=UTF-8'), 
                        ('Cache-Control: ', 'no-cache; must-revalidate')])
            expected = json.loads('{ "playing_order" : "bla" , "volume" : 1, "muted" : true, "playing" : false }')
            returned = json.loads(result)
            self.assertEquals(expected, returned)
        finally:
            self.rb.reset_mock()
