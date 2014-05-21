import unittest
import json

from collections import defaultdict
from mock import Mock
from web.rest.player import Page
from utils import Stub

class TestWebPlayer(unittest.TestCase):

    def setUp(self):
        self.rb = Mock()
        self.components = {'RB' : self.rb}
        self.entry = Stub()
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

