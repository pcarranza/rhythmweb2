import unittest
import json

from rhythmweb import controller
from collections import defaultdict
from mock import Mock
from web.rest.playlists import Page

from utils import Stub

class TestWebPlaylist(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.playlist = Stub()
        self.response = Mock()
        self.environ = defaultdict(lambda: '')
        self.params = defaultdict(lambda: '')

    def test_build(self):
        page = Page()
        self.assertIsNotNone(page)

    def test_basic_do_get_list_returns_one_element(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "playlists" : [ { "id" : "id" , "name" : "name" , "type" : "source_type" , "is_group" : "is_group" , "is_playing" : "is_playing" , "visibility" : "visibility"  } ] }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_with_playlist_returns_right_element(self):
        page = Page()
        self.environ['PATH_PARAMS'] = '0'
        self.rb.get_playlists.return_value = [self.playlist]
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "id" : "id" , "name" : "name" , "type" : "source_type" , "is_group" : "is_group" , "is_playing" : "is_playing" , "visibility" : "visibility"  }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_without_playlists_returns_error(self):
        page = Page()
        self.rb.get_playlists.return_value = []
        self.environ['PATH_PARAMS'] = '0'
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('404 NOT FOUND',
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_with_wrong_playlist_id_returns_client_error(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.environ['PATH_PARAMS'] = '1'
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('400 Bad request: there is no playlist with id 1',
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.get_playlists.assert_called_with()

    def test_enqueue_playlist(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.enqueue_source.return_value = 1
        self.params['action'] = 'enqueue'
        self.params['playlist'] = '0'
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "OK" , "count" : 1 }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.enqueue_source.assert_called_with(self.playlist)

    def test_play_playlist_success(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = True
        self.params['action'] = 'play_source'
        self.params['playlist'] = '0'
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "OK" }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.play_source.assert_called_with(self.playlist)

    def test_play_playlist_fails(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        self.params['action'] = 'play_source'
        self.params['playlist'] = '0'
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "BAD" }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.play_source.assert_called_with(self.playlist)
    
    def test_play_source_fails(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        self.params['action'] = 'play_source'
        self.params['source'] = '0'
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "BAD" }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.play_source.assert_called_with(self.playlist)

    def test_play_invalid_source_fails(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        self.params['action'] = 'play_source'
        self.params['source'] = '10'
        result = page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('400 Bad request: there is no playlist with id 10', 
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_play_with_no_source_fails(self):
        page = Page()
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        self.params['action'] = 'play_source'
        page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('400 Bad request: no "source" parameter', 
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_play_with_no_action_fails(self):
        page = Page()
        self.params['source'] = '1'
        page.do_post(self.environ, self.params, self.response)
        self.response.assert_called_with('400 Bad request: no "action" parameter', 
                [('Content-type', 'text/html; charset=UTF-8')])
