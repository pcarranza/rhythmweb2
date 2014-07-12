import unittest
import json

from mock import Mock
from rhythmweb import view, controller
from rhythmweb.server import Server
from utils import Stub, environ, handle_request

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = Server()

    def test_get_without_parameters_fails(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/library'), self.response)
        self.response.assert_called_with('400 Bad Request: no parameters',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_get_without_second_parameter_fails(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/library/artists'), self.response)
        self.response.assert_called_with('400 Bad Request: no parameters',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_basic_do_get(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/library/artists/bla'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "artist" : "bla" , "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'exact-match': True, 'type': 'song', 'artist': 'bla', 'limit': 0})

    def test_invalid_search_type_fails(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/library/calabaza/bla'), self.response)
        self.response.assert_called_with('400 Bad Request: Invalid library filter "calabaza"',
                [('Content-type', 'text/html; charset=UTF-8')])
