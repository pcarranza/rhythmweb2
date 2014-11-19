#!/bin/bash

if [[ ! -f rhythmweb.plugin ]]; then
    echo "This script has to be called from the root folder"
    exit 1
fi
mkdir -p gi
touch gi/__init__.py
echo "
import mock

class GObject(object):
    IO_IN = 'input'
    keep_running = {'keep': True}

    class Object(object):
        pass

    class GObject(object):
        pass

    @classmethod
    def property(*args, **kwargs):
        return mock.Mock()

    @classmethod
    def io_add_watch(cls, socket, event, function):
        cls.running = True
        import threading, select
        def do_the_work():
            values = select.select([socket], [], [])
            if values:
                function.__self__.cgi_server.handle_request()

        t = threading.Thread(target=do_the_work)
        t.start()
        return 1

    @classmethod
    def source_remove(cls, source):
        cls.running = False

class RB(object):
    class RhythmDBPropType(object):
        ENTRY_ID = 'id'
        TITLE = 'title'
        ARTIST = 'artist'
        ALBUM = 'album'
        TRACK_NUMBER = 'track_number'
        DURATION = 'duration'
        RATING = 'rating'
        YEAR = 'year'
        GENRE = 'genre'
        PLAY_COUNT = 'play_count'
        LOCATION = 'location'
        BITRATE = 'bitrate'
        LAST_PLAYED = 'last_played'

        ARTIST_FOLDED = 'ARTIST_FOLDED'
        TITLE_FOLDED = 'TITLE_FOLDED'
        ALBUM_FOLDED = 'ALBUM_FOLDED'
        GENRE_FOLDED = 'GENRE_FOLDED'
        TYPE = 'TYPE'

    class RhythmDBQueryType(object):
        FUZZY_MATCH = 'FUZZY'
        EQUALS = 'EQUALS'
        GREATER_THAN = 'GREATER_THAN'

    class RhythmDBQueryModel(object):

        album_sort_func = 'album_sort_func'

        def __init__(self, db):
            self.db = db
            self.sort_order = None
            self.asc = None

        @classmethod
        def new_empty(cls, db):
            return cls(db)

        def set_sort_order(self, sort_order, arg3, asc):
            self.sort_order = sort_order
            self.asc = asc

        def __iter__(self):
            yield [mock.Mock()]

class GLib(object):
    class PtrArray(object):
        pass

class Peas(object):
    class Activatable(object):
        pass
" > gi/repository.py
touch gobject.py
touch gtk.py
