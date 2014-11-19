import unittest
import json

from mock import Mock
from rhythmweb import view, controller
from rhythmweb.server import Server
from utils import Stub, environ, handle_request, SourceStub

class TestWebPlaylist(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        controller.rb_handler['rb'] = self.rb
        self.playlist = SourceStub()
        self.response = Mock()
        self.app = Server()

    def test_basic_do_get_list_returns_one_element(self):
        self.playlist = Stub(entries=[Stub()])
        self.rb.get_playlists.return_value = [self.playlist]
        result = handle_request(self.app, environ('/rest/playlists'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{"playlists": [{"entries": [{"title": "title", "album": "album", "last_played": "last_played", "duration": "duration", "artist": "artist", "play_count": "play_count", "rating": "rating", "location": "location", "bitrate": "bitrate", "track_number": "track_number", "id": "id", "genre": "genre", "year": "year"}], "type": "source_type", "id": "id", "name": "name" }]}')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_with_playlist_returns_right_element(self):
        self.playlist = Stub(entries=[Stub()])
        self.rb.get_playlists.return_value = [self.playlist]
        result = handle_request(self.app, environ('/rest/playlists/0'), self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "id" : "id" , "name" : "name" , "type" : "source_type", "entries" : [{"last_played": "last_played", "title": "title", "genre": "genre", "album": "album", "bitrate": "bitrate", "track_number": "track_number", "id": "id", "duration": "duration", "year": "year", "play_count": "play_count", "location": "location", "artist": "artist", "rating": "rating"}]}')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_without_playlists_returns_error(self):
        self.rb.get_playlists.return_value = []
        result = handle_request(self.app, environ('/rest/playlists/0'), self.response)
        self.response.assert_called_with('404 NOT FOUND',
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.get_playlists.assert_called_with()

    def test_basic_do_get_with_wrong_playlist_id_returns_client_error(self):
        self.playlist = Stub(entries=[Stub()])
        self.rb.get_playlists.return_value = [self.playlist]
        result = handle_request(self.app, environ('/rest/playlists/1'), self.response)
        self.response.assert_called_with('400 Bad Request: there is no playlist with id 1',
                [('Content-type', 'text/html; charset=UTF-8')])
        self.rb.get_playlists.assert_called_with()

    def test_post_invalid_action(self):
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=invalid&playlist=0'), 
                self.response)
        self.response.assert_called_with('400 Bad Request: Unknown action invalid',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_enqueue_playlist(self):
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.enqueue_source.return_value = 1
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=enqueue&playlist=0'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "OK" , "count" : 1 }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.enqueue_source.assert_called_with(self.playlist)

    def test_play_playlist_success(self):
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = True
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=play_source&playlist=0'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "OK" }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.play_source.assert_called_with(self.playlist)

    def test_play_playlist_fails(self):
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=play_source&playlist=0'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "BAD" }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.play_source.assert_called_with(self.playlist)
    
    def test_play_source_fails(self):
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=play_source&source=0'), 
                self.response)
        self.response.assert_called_with('200 OK',
                [('Content-type', 'application/json; charset=UTF-8'),
                    ('Cache-Control: ', 'no-cache; must-revalidate')])
        expected = json.loads('{ "result" : "BAD" }')
        returned = json.loads(result)
        self.assertEquals(expected, returned)
        self.rb.play_source.assert_called_with(self.playlist)

    def test_play_invalid_source_fails(self):
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=play_source&source=10'), 
                self.response)
        self.response.assert_called_with('400 Bad Request: there is no playlist with id 10', 
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_play_with_no_source_fails(self):
        self.rb.get_playlists.return_value = [self.playlist]
        self.rb.play_source.return_value = False
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='action=play_source'), 
                self.response)
        self.response.assert_called_with('400 Bad Request: no "source" parameter', 
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_play_with_no_action_fails(self):
        result = handle_request(self.app, 
                environ('/rest/playlists', post_data='source=1'), 
                self.response)
        self.response.assert_called_with('400 Bad Request: no "action" parameter', 
                [('Content-type', 'text/html; charset=UTF-8')])
