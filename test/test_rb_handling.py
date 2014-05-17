import unittest

from contextlib import contextmanager
from mock import Mock
from rbhandle import RBHandler


class RBHandlerTest(unittest.TestCase):

    def test_build_object_success(self):
        shell = Mock()
        self.assertIsNotNone(RBHandler(shell))

    def test_build_object_without_shell_fails(self):
        with self.assertRaises(Exception):
            RBHandle(None)


class RBPlayerTest(unittest.TestCase):

    def setUp(self):
        player = Mock()
        shell = Mock()
        shell.props.shell_player = player
        self.player, self.shell = player, shell

    def test_playing_status(self):
        try:
            rbplayer = RBHandler(self.shell)
            self.player.get_playing.return_value = (None, True)
            self.assertTrue(rbplayer.get_playing_status())
            self.player.get_playing.return_value = (None, False)
            self.assertFalse(rbplayer.get_playing_status())
        finally:
            self.player.reset_mock()

    def test_get_mute(self):
        try:
            rbplayer = RBHandler(self.shell)
            self.player.get_mute.return_value = (None, True)
            self.assertTrue(rbplayer.get_mute())
            self.player.get_mute.return_value = (None, False)
            self.assertFalse(rbplayer.get_mute())
        finally:
            self.player.reset_mock()

    def test_get_volume(self):
        try:
            rbplayer = RBHandler(self.shell)
            self.player.get_volume.return_value = (None, 1.0)
            self.assertEquals(rbplayer.get_volume(), 1.0)
            self.player.get_volume.return_value = (None, 0.5)
            self.assertEquals(rbplayer.get_volume(), 0.5)
        finally:
            self.player.reset_mock()

    def test_playing_entry(self):
        try:
            rbplayer = RBHandler(self.shell)
            self.player.get_playing_entry.return_value = None
            self.assertIsNone(rbplayer.get_playing_entry_id())
            entry = Mock()
            entry.get_ulong.return_value = 1
            self.player.get_playing_entry.return_value = entry
            self.assertEquals(rbplayer.get_playing_entry_id(), 1)
        finally:
            self.player.reset_mock()

