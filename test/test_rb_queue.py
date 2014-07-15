import unittest

from mock import Mock, MagicMock, patch, call
from rbhandle import RBHandler, InvalidQueryException

from utils import EntryStub, ModelStub, Stub

class TestRBHandleQueue(unittest.TestCase):

    def setUp(self):
        (player, shell, db) = Mock(), Mock(), Mock()
        shell.props.shell_player = player
        shell.props.db = db
        self.player, self.shell, self.db = player, shell, db
        self.db.entry_lookup_by_id.side_effect = lambda x: x

    def test_enqueue_one_works_ok(self):
        rb = RBHandler(self.shell)
        rb.enqueue(1)
        self.shell.props.queue_source.add_entry.assert_has_calls([
            call(1, -1)])

    def test_enqueue_many_works_ok(self):
        rb = RBHandler(self.shell)
        rb.enqueue([1, 2])
        self.shell.props.queue_source.add_entry.assert_has_calls([
            call(1, -1), call(2, -1)])

    def test_enqueue_rb_entry_ok(self):
        rb = RBHandler(self.shell)
        rb.enqueue(Stub(id=1))
        self.shell.props.queue_source.add_entry.assert_has_calls([
            call(1, -1)])

    def test_shuffle_queue(self):
        self.shell.props.queue_source.props.query_model = ModelStub(
            EntryStub(1), EntryStub(2), EntryStub(3))
        rb = RBHandler(self.shell)
        rb.shuffle_queue()
        expected = set([1, 2, 3])
        for args in self.shell.props.queue_source.move_entry.call_args_list:
            key = args[0][0]
            expected.remove(key)
        self.assertTrue(not expected)

    def test_dequeue_one_works_ok(self):
        self.shell.props.queue_source.props.query_model = ModelStub(
            EntryStub(1), EntryStub(2), EntryStub(3))
        rb = RBHandler(self.shell)
        rb.dequeue(1)
        self.shell.props.queue_source.remove_entry.assert_has_calls([
            call(1)])
            
    def test_dequeue_many_works_ok(self):
        self.shell.props.queue_source.props.query_model = ModelStub(
            EntryStub(1), EntryStub(2), EntryStub(3))
        rb = RBHandler(self.shell)
        rb.dequeue([1, 2])
        self.shell.props.queue_source.remove_entry.assert_has_calls([
            call(1), call(2)])
            
    def test_get_play_queue_works(self):
        self.shell.props.queue_source.props.query_model = ModelStub(
            EntryStub(1), EntryStub(2), EntryStub(5))
        rb = RBHandler(self.shell)
        play_queue = rb.get_play_queue()
        self.assertEquals(play_queue[0].id, 1)
        self.assertEquals(play_queue[1].id, 2)
        self.assertEquals(play_queue[2].id, 5)
