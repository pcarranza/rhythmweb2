import unittest

from mock import Mock, patch
from rhythmweb import view, controller, rb
from rhythmweb.server import Server
from utils import Stub, environ, handle_request

class TestWebPlayer(unittest.TestCase):

    def setUp(self):
        self.rb = Mock(rb.RBHandler)
        controller.rb_handler['rb'] = self.rb
        self.response = Mock()
        self.app = Server()

        self.queue_patch = patch('rhythmweb.controller.rb.Queue', spec=rb.Queue)
        self.queue_class = self.queue_patch.start()
        self.queue = Mock(spec=rb.Queue)
        self.queue_class.return_value = self.queue

    def tearDown(self):
        self.queue_patch.stop()

    def test_do_get_errs(self):
        result = handle_request(self.app, environ('/rest/player'), self.response)
        self.response.assert_called_with('405 method GET not allowed',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_post_without_action_fails(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='actions=invalid'),
                self.response)
        self.response.assert_called_with('400 Bad Request: No action', 
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_post_invalid_action_fails(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=invalid'),
                self.response)
        self.response.assert_called_with('400 Bad Request: action "invalid" is not supported', 
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_post_play_pause_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=play_pause'),
                self.response)
        self.rb.play_pause.assert_called_with()
        self.rb.get_playing_status.assert_called_with()

    def test_post_next_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=next'),
                self.response)
        self.rb.play_next.assert_called_with()
        self.rb.get_playing_status.assert_called_with()

    def test_post_previous_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=previous'),
                self.response)
        self.rb.previous.assert_called_with()
        self.rb.get_playing_status.assert_called_with()

    def test_post_seek_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=seek&time=10'),
                self.response)
        self.rb.seek.assert_called_with(10)
        self.rb.get_playing_status.assert_called_with()

    def test_post_enqueue_with_one_value_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=enqueue&entry_id=1'),
                self.response)
        self.queue.enqueue.assert_called_with([1])
        self.rb.get_playing_status.assert_called_with()

    def test_post_enqueue_with_many_values_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=enqueue&entry_id=1,2'),
                self.response)
        self.queue.enqueue.assert_called_with([1, 2])
        self.rb.get_playing_status.assert_called_with()

    def test_post_dequeue_with_one_value_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=dequeue&entry_id=1'),
                self.response)
        self.queue.dequeue.assert_called_with([1])
        self.rb.get_playing_status.assert_called_with()

    def test_post_dequeue_with_many_values_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=dequeue&entry_id=1,2'),
                self.response)
        self.queue.dequeue.assert_called_with([1, 2])
        self.rb.get_playing_status.assert_called_with()

    def test_post_shuffle_queue_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=shuffle_queue'),
                self.response)
        self.queue.shuffle_queue.assert_called_with()
        self.rb.get_playing_status.assert_called_with()

    def test_post_clear_queue_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=clear_queue'),
                self.response)
        self.queue.clear_play_queue.assert_called_with()
        self.rb.get_playing_status.assert_called_with()

    def test_post_play_entry_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=play_entry&entry_id=1'),
                self.response)
        self.rb.play_entry.assert_called_with(1)
        self.rb.get_playing_status.assert_called_with()

    def test_post_mute_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=mute'),
                self.response)
        self.rb.toggle_mute.assert_called_with()
        self.rb.get_playing_status.assert_called_with()

    def test_post_set_volume_works(self):
        result = handle_request(self.app, 
                environ('/rest/player', post_data='action=set_volume&volume=0.5'),
                self.response)
        self.rb.set_volume.assert_called_with(0.5)
        self.rb.get_playing_status.assert_called_with()
