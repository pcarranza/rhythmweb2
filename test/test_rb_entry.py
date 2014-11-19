import unittest

from mock import Mock, patch
from rhythmweb.rb import RBHandler

from utils import EntryStub, ModelStub, Stub


class TestRBEntry(unittest.TestCase):

    def setUp(self):
        (player, shell, db) = Mock(), Mock(), Mock()
        shell.props.shell_player = player
        shell.props.db = db
        self.player, self.shell, self.db = player, shell, db
        self.db.entry_lookup_by_id.side_effect = lambda x: EntryStub(x)

    def test_set_rating_works(self):
        rbplayer = RBHandler(self.shell)
        self.db.entry_lookup_by_id.side_effect = lambda x: x
        rbplayer.set_rating(1, 5)
        self.db.entry_set.assert_called_with(1, 'rating', 5)

    def test_set_rating_with_invalid_value_fails(self):
        rbplayer = RBHandler(self.shell)
        with self.assertRaises(Exception):
            rbplayer.set_rating(1, 'x')

    def test_get_entry_works(self):
        rbplayer = RBHandler(self.shell)
        entry = rbplayer.get_entry(1)
        self.assertEquals(entry.id, 1)

