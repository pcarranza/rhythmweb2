import unittest

from contextlib import contextmanager
from mock import Mock
from rbhandle import RBHandler, ORDER_SHUFFLE, ORDER_LINEAR


class RBBasicHandlerTest(unittest.TestCase):

    def test_build_object_success(self):
        shell = Mock()
        self.assertIsNotNone(RBHandler(shell))

    def test_build_object_without_shell_fails(self):
        with self.assertRaises(Exception):
            RBHandle(None)


class RBTest(unittest.TestCase):

    def setUp(self):
        (player, shell, db) = Mock(), Mock(), Mock()
        shell.props.shell_player = player
        shell.props.db = db
        self.player, self.shell, self.db = player, shell, db

    def test_playing_status(self):
        rbplayer = RBHandler(self.shell)
        self.player.get_playing.return_value = (None, True)
        self.assertTrue(rbplayer.get_playing_status())
        self.player.get_playing.return_value = (None, False)
        self.assertFalse(rbplayer.get_playing_status())

    def test_get_mute(self):
        rbplayer = RBHandler(self.shell)
        self.player.get_mute.return_value = (None, True)
        self.assertTrue(rbplayer.get_mute())
        self.player.get_mute.return_value = (None, False)
        self.assertFalse(rbplayer.get_mute())

    def test_toggle_mute(self):
        rbplayer = RBHandler(self.shell)
        rbplayer.toggle_mute()
        self.player.toggle_mute.assert_called_with()

    def test_get_volume(self):
        rbplayer = RBHandler(self.shell)
        self.player.get_volume.return_value = (None, 1.0)
        self.assertEquals(rbplayer.get_volume(), 1.0)
        self.player.get_volume.return_value = (None, 0.5)
        self.assertEquals(rbplayer.get_volume(), 0.5)

    def test_set_volume_with_invalid_value_fails(self):
        rbplayer = RBHandler(self.shell)
        with self.assertRaises(Exception):
            rbplayer.set_volume('1')

    def test_set_volume_calls_player(self):
        rbplayer = RBHandler(self.shell)
        rbplayer.set_volume(2.0)
        self.player.set_volume.assert_called_with(2.0)

    def test_playing_entry(self):
        rbplayer = RBHandler(self.shell)
        self.player.get_playing_entry.return_value = None
        self.assertIsNone(rbplayer.get_playing_entry_id())
        entry = Mock()
        entry.get_ulong.return_value = 1
        self.player.get_playing_entry.return_value = entry
        self.assertEquals(rbplayer.get_playing_entry_id(), 1)

    def test_get_playing_time_calls_player(self):
        self.player.get_playing_time.return_value = (None, 10)
        rbplayer = RBHandler(self.shell)
        self.assertEquals(rbplayer.get_playing_time(), 10)

    def test_get_playing_time_string_calls_player(self):
        self.player.get_playing_time_string.return_value = 'bla'
        rbplayer = RBHandler(self.shell)
        self.assertEquals(rbplayer.get_playing_time_string(), 'bla')

    def test_play_next_works(self):
        self.player.get_playing.return_value = (None, True)
        rbplayer = RBHandler(self.shell)
        rbplayer.play_next()
        self.player.do_next.assert_called_with()

    def test_play_previous_works(self):
        self.player.get_playing.return_value = (None, True)
        rbplayer = RBHandler(self.shell)
        rbplayer.previous()
        self.player.do_previous.assert_called_with()

    def test_seek(self):
        rbplayer = RBHandler(self.shell)
        rbplayer.seek(15)
        self.player.seek.assert_called_with(15)

    def test_play_pause(self):
        self.player.get_playing.return_value = (None, True)
        self.player.playpause.return_value = 1
        rbplayer = RBHandler(self.shell)
        self.assertEquals(rbplayer.play_pause(), 1)
        self.player.playpause.assert_called_with(False)

    def test_play_entry_with_invalid_id_fails(self):
        rbplayer = RBHandler(self.shell)
        with self.assertRaises(Exception):
            rbplayer.play_entry('invalid')

    def test_play_entry_with_none_as_id_fails(self):
        rbplayer = RBHandler(self.shell)
        with self.assertRaises(Exception):
            rbplayer.play_entry(None)

    def test_play_entry_with_valid_id_works(self):
        entry = Mock()
        source = Mock()
        self.player.props.queue_source = source
        self.player.get_playing.return_value = (None, True)
        self.db.entry_lookup_by_id.return_value = entry
        rbplayer = RBHandler(self.shell)
        rbplayer.play_entry(1)
        self.player.play_entry.assert_called_with(entry, source)

    def test_toggle_shuffle(self):
        rbplayer = RBHandler(self.shell)
        rbplayer.set_play_order(ORDER_LINEAR)
        rbplayer.toggle_shuffle()
        self.assertEquals(rbplayer.get_play_order(), ORDER_SHUFFLE)

    def test_toggle_loop(self):
        rbplayer = RBHandler(self.shell)
        rbplayer.set_play_order(ORDER_SHUFFLE)
        rbplayer.toggle_loop()
        self.assertEquals(rbplayer.get_play_order(), 'shuffle-loop')

