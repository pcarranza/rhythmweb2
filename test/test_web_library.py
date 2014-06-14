import unittest
import json

from rhythmweb import controller
from collections import defaultdict
from mock import Mock
from web.rest.library import Page
from rbhandle.query import InvalidQueryException

from utils import Stub

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.environ = defaultdict(lambda: '')
        self.params = defaultdict(lambda: '')

    def test_build(self):
        page = Page()
        self.assertIsNotNone(page)

    def test_basic_do_get(self):
        page = Page()
        self.environ['PATH_PARAMS'] = 'artists/bla'
        self.rb.query.return_value = [self.entry]
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "artist" : "bla" , "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'exact-match': True, 'type': 'song', 'artist': 'bla', 'limit': 0})

