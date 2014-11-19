import unittest

from mock import Mock
from rhythmweb.rb import RBHandler
from utils import ModelStub, EntryStub

class TestRBSource(unittest.TestCase):

    def setUp(self):
        (player, shell, db) = Mock(), Mock(), Mock()
        shell.props.shell_player = player
        shell.props.db = db
        self.player, self.shell, self.db = player, shell, db
        self.db.entry_lookup_by_id.side_effect = lambda x: x

    def test_get_source_with_index_returns_none(self):
        rb = RBHandler(self.shell)
        source = rb.get_source(1)
        self.assertIsNone(source)

    def test_get_source_entries(self):
        rb = RBHandler(self.shell)
        source = Mock()
        source.query_model =  ModelStub(EntryStub(1), EntryStub(2), EntryStub(3))
        rb.load_source_entries(source)
        entries = source.entries
        entries = [entry.id for entry in entries]
        self.assertListEqual(entries, [1, 2, 3])

    def test_play_source(self):
        self.player.get_playing.return_value = (None, True)
        rb = RBHandler(self.shell)
        source = Mock()
        self.assertTrue(rb.play_source(source))
        self.shell.props.shell_player.set_playing_source.assert_called_with(source.source)

    def test_get_playlists(self):
        self.shell.props.playlist_manager.get_playlists.return_value = [Mock()]
        rb = RBHandler(self.shell)
        playlists = rb.get_playlists()
        self.assertEquals(len(playlists), 1)
