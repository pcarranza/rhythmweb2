import unittest

from mock import Mock
from rbhandle import RBHandler
from utils import EntryStub

class TestRBLibrary(unittest.TestCase):

    def setUp(self):
        (player, shell, db) = Mock(), Mock(), Mock()
        shell.props.shell_player = player
        shell.props.db = db
        self.player, self.shell, self.db = player, shell, db

    def test_entry_added_signal_connected(self):
        rb = RBHandler(self.shell)
        self.shell.props.db.connect.assert_called_with(
                'entry_added', rb.library.entry_added)

    def test_one_entry_added_adds_values(self):
        rb = RBHandler(self.shell)
        rb.library.entry_added(self.shell.props.db, 
                EntryStub(1, artist='guy 1', album='album 1',
                genre='genre 1', title='song 1', play_count=10))
        self.assertEquals(rb.library.artists, {'values': {'guy 1': 10}, 'max': 10})
        self.assertEquals(rb.library.albums, {'values': {'album 1': 10}, 'max': 10})
        self.assertEquals(rb.library.genres, {'values': {'genre 1': 10}, 'max': 10})
        self.assertEquals(rb.library.songs, {'values': {'song 1': 10}, 'max': 10})

    def test_many_entries_added_adds_values(self):
        rb = RBHandler(self.shell)
        rb.library.entry_added(self.shell.props.db, 
                EntryStub(1, artist='guy 1', album='album 1',
                genre='genre 1', title='song 1', play_count=10))
        rb.library.entry_added(self.shell.props.db, 
                EntryStub(1, artist='guy 2', album='album 1',
                genre='genre 1', title='song 2', play_count=5))
        rb.library.entry_added(self.shell.props.db, 
                EntryStub(1, artist='guy 1', album='album 1',
                genre='genre 1', title='song 3', play_count=7))
        self.assertEquals(rb.library.artists, {'values': {'guy 1': 17, 'guy 2' : 5}, 'max': 17})
        self.assertEquals(rb.library.albums, {'values': {'album 1': 22}, 'max': 22})
        self.assertEquals(rb.library.genres, {'values': {'genre 1': 22}, 'max': 22})
        self.assertEquals(rb.library.songs, {'values': {'song 1': 10, 'song 2': 5, 'song 3': 7}, 'max': 10})
