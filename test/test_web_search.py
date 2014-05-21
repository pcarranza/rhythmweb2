import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.search import Page

from utils import Stub

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_basic_do_get(self):
        page = Page(self.components)
        entry = Stub()
        response = Mock()
        environ = defaultdict(lambda: '')
        self.rb.query.return_value = [entry]
        result = page.do_get(environ, response)
        response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({})

    def test_post_search(self):
        page = Page(self.components)
        entry = Stub()
        response = Mock()
        environ = defaultdict(lambda: '')
        params = defaultdict(lambda: '')
        self.rb.query.return_value = [entry]
        result = page.do_post(environ, params, response)
        response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({})

    def test_query_with_params_and_limit(self):
        page = Page(self.components)
        entry = Stub()
        response = Mock()
        environ = defaultdict(lambda: '')
        environ['PATH_PARAMS'] = 'song/limit/10/first/5'
        self.rb.query.return_value = [entry for i in range(5)]
        result = page.do_get(environ, response)
        response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.assertEquals(5, len(returned['entries']))
        self.rb.query.assert_called_with({ 'type' : 'song', 'limit' : '10', 'first' : '5' })

    def test_get_search_returns_empty_set(self):
        page = Page(self.components)
        entry = Stub()
        response = Mock()
        environ = defaultdict(lambda: '')
        self.rb.query.return_value = []
        result = page.do_get(environ, response)
        response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        returned = json.loads(result)
        self.assertEquals({}, returned)
        self.rb.query.assert_called_with({})

    def test_post_search_with_post_params(self):
        page = Page(self.components)
        entry = Stub()
        response = Mock()
        environ = defaultdict(lambda: '')
        params = defaultdict(lambda: '')
        params['album'] = 'calabaza'
        params['title'] = 'oruga'
        params['artist'] = 'uno'
        params['type'] = 'song'
        params['genre'] = 'classic'
        params['rating'] = '4'
        self.rb.query.return_value = [entry]
        result = page.do_post(environ, params, response)
        response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "entries" : [ { "duration" : "duration" , "location" : "location" , "last_played" : "last_played" , "album" : "album" , "title" : "title" , "genre" : "genre" , "year" : "year" , "rating" : "rating" , "id" : "id" , "track_number" : "track_number" , "play_count" : "play_count" , "bitrate" : "bitrate" , "artist" : "artist"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.query.assert_called_with({'artist': 'uno', 'title': 'oruga', 'rating': 4, 'album': 'calabaza', 'type': 'song', 'genre': 'classic'})

