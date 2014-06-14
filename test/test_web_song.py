import unittest
import json

from mock import Mock
from rhythmweb import controller
from utils import Stub, cgi_application, environ, handle_request

class TestWebSong(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.response = Mock()
        self.app = cgi_application()

    def test_get_invalid_song_returns_not_found(self):
        self.rb.get_entry.return_value = None
        result = handle_request(self.app, environ('/rest/song/1'), self.response)
        self.response.assert_called_with('404 NOT FOUND',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_get_song_success(self):
        self.rb.load_entry.return_value = Stub(1)
        result = handle_request(self.app, environ('/rest/song/1'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        expected = json.loads('{ "play_count" : "play_count" , "album" : "album" , "track_number" : "track_number" , "rating" : "rating" , "last_played" : "last_played" , "location" : "location" , "id" : 1, "bitrate" : "bitrate" , "year" : "year" , "duration" : "duration" , "title" : "title" , "genre" : "genre" , "artist" : "artist"  }')
        self.assertEquals(expected, returned)

    def test_rate_invalid_song_fails(self):
        self.rb.get_entry.return_value = None
        result = handle_request(self.app, environ('/rest/song/2', post_data='rating=5'), self.response)
        self.response.assert_called_with('404 NOT FOUND',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_rate_song_success(self):
        self.rb.load_entry.return_value = Stub(2)
        result = handle_request(self.app, environ('/rest/song/2', post_data='rating=5'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "play_count" : "play_count" , "album" : "album" , "track_number" : "track_number" , "rating" : 5, "last_played" : "last_played" , "location" : "location" , "id" : 2, "bitrate" : "bitrate" , "year" : "year" , "duration" : "duration" , "title" : "title" , "genre" : "genre" , "artist" : "artist"  }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.set_rating.assert_called_with(2, 5)

    def test_post_invalid_song_id_errs(self):
        result = handle_request(self.app, environ('/rest/song/X', post_data='rating=5'), self.response)
        self.response.assert_called_with('400 Bad Request: song id is not a number',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_post_invalid_rating_errs(self):
        result = handle_request(self.app, environ('/rest/song/1', post_data='rating=x'), self.response)
        self.response.assert_called_with('400 Bad Request: rating must be a number',
                [('Content-type', 'text/html; charset=UTF-8')])
