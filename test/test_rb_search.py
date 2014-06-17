import unittest

from mock import Mock, MagicMock, patch, call
from rbhandle import RBHandler


@patch('gi.repository.RB.RhythmDBQueryModel.new_empty')
@patch('gi.repository.GLib.PtrArray')
class TestRBHandleSearch(unittest.TestCase):

    def setUp(self):
        (player, shell, db) = Mock(), Mock(), Mock()
        shell.props.shell_player = player
        shell.props.db = db
        self.player, self.shell, self.db = player, shell, db
        def echo(value):
            return value
        db.entry_type_get_by_name.side_effect = echo

    def test_search_song(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub([item])
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.search_song('bla')

        self.assertEquals(model.sort_order, 'album_sort_func')
        self.assertFalse(model.desc)
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'EQUALS', 'TYPE', 'song'),
            call(array, 'FUZZY', 'ARTIST_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'song'),
            call(array, 'FUZZY', 'TITLE_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'song'),
            call(array, 'FUZZY', 'ALBUM_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'song'),
            call(array, 'FUZZY', 'GENRE_FOLDED', 'bla')])

    def test_search_radio(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub([item])
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.search_radio('bla')

        self.assertEquals(model.sort_order, 'album_sort_func')
        self.assertFalse(model.desc)
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'EQUALS', 'TYPE', 'iradio'),
            call(array, 'FUZZY', 'ARTIST_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'iradio'),
            call(array, 'FUZZY', 'TITLE_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'iradio'),
            call(array, 'FUZZY', 'ALBUM_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'iradio'),
            call(array, 'FUZZY', 'GENRE_FOLDED', 'bla')])

    def test_search_podcast(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub([item])
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.search_podcast('bla')

        self.assertEquals(model.sort_order, 'album_sort_func')
        self.assertFalse(model.desc)
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'EQUALS', 'TYPE', 'podcast-post'),
            call(array, 'FUZZY', 'ARTIST_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'podcast-post'),
            call(array, 'FUZZY', 'TITLE_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'podcast-post'),
            call(array, 'FUZZY', 'ALBUM_FOLDED', 'bla'),
            call(array, 'EQUALS', 'TYPE', 'podcast-post'),
            call(array, 'FUZZY', 'GENRE_FOLDED', 'bla')])

    def test_query_with_rating_exact_match_and_play_count(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub([item])
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.query({'rating': 5, 'play_count': 2, 'exact-match': True, 'first': 3, 'limit': 1})
        self.assertEquals(model.sort_order, 'album_sort_func')
        self.assertFalse(model.desc)
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'EQUALS', 'TYPE', 'song'),
            call(array, 'GREATER_THAN', 7, 5.0),
            call(array, 'GREATER_THAN', 10, 2)])



class ModelStub(object):

    def __init__(self, *rows):
        self.rows = rows
        self.sort_order = None
        self.desc = None

    def __getitem__(self, key):
        return self.rows[key]

    def set_sort_order(self, sort_order, arg3, desc):
        self.sort_order = sort_order
        self.desc = desc
