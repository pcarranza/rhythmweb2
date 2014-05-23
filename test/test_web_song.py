import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.song import Page
from utils import Stub

class TestWebStatus(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}
        self.response = Mock()
        self.environ = defaultdict(lambda: '')
        self.params = defaultdict(lambda: '')

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_get_song_success(self):
        self.environ['PATH_PARAMS'] = '1'
        self.rb.load_entry.return_value = Stub(1)
        page = Page(self.components)
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK', 
                [('Content-type', 'application/json; charset=UTF-8'), 
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        expected = json.loads('{ "play_count" : "play_count" , "album" : "album" , "track_number" : "track_number" , "rating" : "rating" , "last_played" : "last_played" , "location" : "location" , "id" : 1, "bitrate" : "bitrate" , "year" : "year" , "duration" : "duration" , "title" : "title" , "genre" : "genre" , "artist" : "artist"  }')
        self.assertEquals(expected, returned)

    def test_rate_song_success(self):
        self.environ['PATH_PARAMS'] = '2'
        self.params['rating'] = '5'
        self.rb.load_entry.return_value = Stub(2)
        page = Page(self.components)
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "play_count" : "play_count" , "album" : "album" , "track_number" : "track_number" , "rating" : "rating" , "last_played" : "last_played" , "location" : "location" , "id" : 2, "bitrate" : "bitrate" , "year" : "year" , "duration" : "duration" , "title" : "title" , "genre" : "genre" , "artist" : "artist"  }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.set_rating.assert_called_with(2, 5)
