import unittest

from collections import defaultdict
from mock import Mock
from web.rest.player import Page
from utils import Stub

class TestWebPlayer(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}
        self.rb.load_entry.return_value = Stub()
        self.response = Mock()
        self.environ = defaultdict(lambda: '')

    def test_build(self):
        page = Page(self.components)
        self.assertIsNotNone(page)

    def test_do_get_errs(self):
        page = Page(self.components)
        page.do_get(self.environ, self.response)
        self.response.assert_called_with('405 method GET not allowed',
                [('Content-type', 'text/html; charset=UTF-8')])

    def test_post_play_pause_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'play_pause'},
                response=self.response)
        self.rb.play_pause.assert_called_with()

    def test_post_previous_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'next'},
                response=self.response)
        self.rb.play_next.assert_called_with()

    def test_post_previous_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'previous'},
                response=self.response)
        self.rb.previous.assert_called_with()

    def test_post_seek_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'seek', 'time' : 10},
                response=self.response)
        self.rb.seek.assert_called_with(10)

    def test_post_enqueue_with_one_value_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'enqueue', 'entry_id' : 1},
                response=self.response)
        self.rb.enqueue.assert_called_with([1])

    def test_post_enqueue_with_many_values_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'enqueue', 'entry_id' : [1, 2]},
                response=self.response)
        self.rb.enqueue.assert_called_with([1, 2])

    def test_post_dequeue_with_one_value_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'dequeue', 'entry_id' : 1},
                response=self.response)
        self.rb.dequeue.assert_called_with([1])

    def test_post_dequeue_with_many_values_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'dequeue', 'entry_id' : [1, 2]},
                response=self.response)
        self.rb.dequeue.assert_called_with([1, 2])

    def test_post_shuffle_queue_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'shuffle_queue'},
                response=self.response)
        self.rb.shuffle_queue.assert_called_with()

    def test_post_clear_queue_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'clear_queue'},
                response=self.response)
        self.rb.clear_play_queue.assert_called_with()

    def test_post_play_entry_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'play_entry', 'entry_id' : 1},
                response=self.response)
        self.rb.play_entry.assert_called_with(1)

    def test_post_mute_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'mute'},
                response=self.response)
        self.rb.toggle_mute.assert_called_with()

    def test_post_set_volume_works(self):
        page = Page(self.components)
        result = page.do_post(self.environ, post_params={'action' : 'set_volume', 'volume' : 0.5},
                response=self.response)
        self.rb.set_volume.assert_called_with(0.5)
