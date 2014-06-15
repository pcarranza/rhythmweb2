import unittest
import json

from mock import Mock
from rhythmweb import controller
from rbhandle import InvalidQueryException
from utils import Stub, cgi_application, environ, handle_request

from utils import Stub

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.entry = Stub()
        self.response = Mock()
        self.app = cgi_application()

    def test_basic_do_get(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/search'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({})

    def test_post_search(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, environ('/rest/search', post_data=''), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({})

    def test_query_with_params_and_limit(self):
        self.rb.query.return_value = [self.entry for i in range(5)]
        result = handle_request(self.app, 
                environ('/rest/search/song/limit/10/first/5'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.assertEquals(5, len(returned['entries']))
        self.rb.query.assert_called_with({ 'type' : 'song', 'limit' : '10', 'first' : '5' })

    def test_get_search_returns_empty_set(self):
        self.rb.query.return_value = []
        result = handle_request(self.app, 
                environ('/rest/search'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.assertEquals({}, returned)
        self.rb.query.assert_called_with({})

    def test_post_search_with_post_params(self):
        self.rb.query.return_value = [self.entry]
        post_data = '&'.join(('album=calabaza', 'title=oruga', 'artist=uno', 'type=song', 
                  'genre=classic', 'rating=4', 'first=1', 'limit=10'))
        result = handle_request(self.app, 
                environ('/rest/search', post_data=post_data), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'type': 'song', 'limit': '10', 'rating': 4, 'album': 'calabaza', 'title': 'oruga', 'first': '1', 'genre': 'classic', 'artist': 'uno'})

    def test_post_invalid_type(self):
        self.rb.query.return_value = [self.entry]
        result = handle_request(self.app, 
                environ('/rest/search', post_data='type=calabaza'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'type': None})

    def test_get_invalid_query(self):
        self.rb.query.side_effect = InvalidQueryException('Invalid query')
        result = handle_request(self.app, 
                environ('/rest/search/song'), 
                self.response)
        self.response.assert_called_with('400 Bad request: Invalid query', 
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.query.assert_called_with({'type': 'song'})
