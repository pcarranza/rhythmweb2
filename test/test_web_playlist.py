import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.playlists import Page

from utils import Stub

class TestWebSearch(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}
        self.playlist = Stub()
        self.response = Mock()
        self.environ = defaultdict(lambda: '')
        self.params = defaultdict(lambda: '')

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_basic_do_get_list_returns_one_element(self):
        page = Page(self.components)
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
        page = Page(self.components)
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
        page = Page(self.components)
        self.rb.get_playlists.return_value = []
        self.environ['PATH_PARAMS'] = '0'
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('404 there are no playlists', 
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_with_wrong_playlist_id_returns_client_error(self):
        page = Page(self.components)
        self.rb.get_playlists.return_value = [self.playlist]
        self.environ['PATH_PARAMS'] = '1'
        result = page.do_get(self.environ, self.response)
        self.response.assert_called_with('400 There is no playlist with id 1', 
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.get_playlists.assert_called_with()
