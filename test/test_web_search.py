import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.search import Page
from rbhandle.query import InvalidQueryException

from utils import Stub

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}
        self.entry = Stub()
        self.response = Mock()
        self.environ = defaultdict(lambda: '')
        self.params = defaultdict(lambda: '')

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_basic_do_get(self):
        page = Page(self.components)
        self.rb.query.return_value = [self.entry]
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({})

    def test_post_search(self):
        page = Page(self.components)
        self.rb.query.return_value = [self.entry]
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({})

    def test_query_with_params_and_limit(self):
        page = Page(self.components)
        self.environ['PATH_PARAMS'] = 'song/limit/10/first/5'
        self.rb.query.return_value = [self.entry for i in range(5)]
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.assertEquals(5, len(returned['entries']))
        self.rb.query.assert_called_with({ 'type' : 'song', 'limit' : '10', 'first' : '5' })

    def test_get_search_returns_empty_set(self):
        page = Page(self.components)
        self.rb.query.return_value = []
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.assertEquals({}, returned)
        self.rb.query.assert_called_with({})

    def test_post_search_with_post_params(self):
        page = Page(self.components)
        self.params['album'] = 'calabaza'
        self.params['title'] = 'oruga'
        self.params['artist'] = 'uno'
        self.params['type'] = 'song'
        self.params['genre'] = 'classic'
        self.params['rating'] = '4'
        self.params['first'] = '1'
        self.params['limit'] = '10'
        self.rb.query.return_value = [self.entry]
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'type': 'song', 'limit': '10', 'rating': 4, 'album': 'calabaza', 'title': 'oruga', 'first': '1', 'genre': 'classic', 'artist': 'uno'})

    def test_post_invalid_type(self):
        page = Page(self.components)
        self.params['type'] = 'calabazas'
        self.rb.query.return_value = [self.entry]
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'type': None})

    def test_get_invalid_query(self):
        page = Page(self.components)
        self.rb.query.side_effect = InvalidQueryException('Invalid query')
        self.environ['PATH_PARAMS'] = 'song'
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('400 Bad request: Invalid query', 
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.query.assert_called_with({'type': 'song'})
