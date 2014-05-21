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
        self.entry = Stub()
        self.response = Mock()
        self.environ = defaultdict(lambda: '')

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_get_status_when_not_playing_works(self):
        page = Page(self.components)
        self.rb.get_playing_status.return_value = False
        self.rb.get_play_order.return_value = 'bla'
        self.rb.get_mute.return_value = True
        self.rb.get_volume.return_value = 1
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK', 
                [('Content-type', 'application/json; charset=UTF-8'), 
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "playing_order" : "bla" , "volume" : 1, "muted" : true, "playing" : false }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)

    def test_get_status_when_playing_works(self):
        page = Page(self.components)
        self.rb.get_playing_status.return_value = True
        self.rb.get_play_order.return_value = 'bla'
        self.rb.get_mute.return_value = False
        self.rb.get_volume.return_value = 1
        self.rb.load_entry.return_value = self.entry
        self.rb.get_playing_time.return_value = 10
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK', 
                [('Content-type', 'application/json; charset=UTF-8'), 
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('''{ "playing_entry" : {
                        "artist" : "artist" , "title" : "title" , "duration" : 
                        "duration" , "genre" : "genre" , "id" : "id" , "year" : "year" , 
                        "bitrate" : "bitrate" , "location" : "location" , 
                        "rating" : "rating" , "last_played" : "last_played" , 
                        "play_count" : "play_count" , "track_number" : "track_number" , 
                        "album" : "album"  }, 
                        "playing_order" : "bla" , "muted" : false, 
                        "volume" : 1, "playing" : true, "playing_time" : 10 }''')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
