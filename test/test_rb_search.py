import unittest

from mock import Mock, MagicMock, patch, call
from rbhandle import RBHandler, InvalidQueryException
from utils import ModelStub


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
        array, model = Mock(), ModelStub(item)
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
        array, model = Mock(), ModelStub(item)
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
        array, model = Mock(), ModelStub(item)
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
        array, model = Mock(), ModelStub(item)
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

    def test_query_with_invalid_rating_fails(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        with self.assertRaises(InvalidQueryException):
            rb.query({'rating': 'x'})

    def test_query_with_invalid_play_count_fails(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        with self.assertRaises(InvalidQueryException):
            rb.query({'play_count': 'x'})

    def test_query_with_invalid_first_fails(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        with self.assertRaises(InvalidQueryException):
            rb.query({'first': 'x'})

    def test_query_with_invalid_limit_fails(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        with self.assertRaises(InvalidQueryException):
            rb.query({'limit': 'x'})

    def test_query_with_invalid_type_fails(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        with self.assertRaises(InvalidQueryException):
            rb.query({'type': 'x'})

    def test_query_artist_works(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub(item)
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.query({'artist': 'calabazas'})
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'FUZZY', 'ARTIST_FOLDED', 'calabazas')])

    def test_query_title_works(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub(item)
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.query({'title': 'a song name'})
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'FUZZY', 'TITLE_FOLDED', 'a song name')])

    def test_query_album_works(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub(item)
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.query({'album': 'an album name'})
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'FUZZY', 'ALBUM_FOLDED', 'an album name')])

    def test_query_genre_works(self, ptr_array, query_model):
        item = Mock()
        array, model = Mock(), ModelStub(item)
        query_model.return_value = model
        ptr_array.return_value = array

        rb = RBHandler(self.shell)
        rb.query({'genre': 'a nice genre'})
        self.db.do_full_query_parsed.assert_called_with(model, array)
        self.db.query_append_params.assert_has_calls([
            call(array, 'FUZZY', 'GENRE_FOLDED', 'a nice genre')])

    def test_search_with_no_filters_returns_empty_list(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        result = rb.query({})
        self.assertListEqual(result, [])

    def test_search_with_null_filters_returns_empty_list(self, ptr_array, query_model):
        rb = RBHandler(self.shell)
        result = rb.query(None)
        self.assertListEqual(result, [])


