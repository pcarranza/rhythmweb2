import unittest
import json

from collections import defaultdict
from mock import Mock, patch
from web.rest.search import Page

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_basic_do_get(self):
        try:
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
        finally:
            self.rb.reset_mock()

    def test_post_search(self):
        try:
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
        finally:
            self.rb.reset_mock()

    def test_query_with_params_and_limit(self):
        try:
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
        finally:
            self.rb.reset_mock()

    def test_get_search_returns_empty_set(self):
        try:
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
        finally:
            self.rb.reset_mock()

class Stub(object):
    def __getattr__(self, name):
        return name
