import unittest
import json

from mock import Mock
from rhythmweb import view, controller
from utils import Stub, environ, handle_request
from rhythmweb.server import Server

class TestWebStatus(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = Server()

    def test_get_status_when_not_playing_works(self):
        self.rb.get_playing_status.return_value = False
        self.rb.get_play_order.return_value = 'bla'
        self.rb.get_mute.return_value = True
        self.rb.get_volume.return_value = 1
        result = handle_request(self.app, environ('/rest/status'), self.response)
        self.response.assert_called_with('200 OK', 
                [('Content-type', 'application/json; charset=UTF-8'), 
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "playing_order" : "bla" , "volume" : 1, "muted" : true, "playing" : false }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)

    def test_get_status_when_playing_works(self):
        self.rb.get_playing_status.return_value = True
        self.rb.get_play_order.return_value = 'bla'
        self.rb.get_mute.return_value = False
        self.rb.get_volume.return_value = 1
        self.rb.get_playing_entry.return_value = self.entry
        self.rb.get_playing_time.return_value = 10
        result = handle_request(self.app, environ('/rest/status'), self.response)
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
