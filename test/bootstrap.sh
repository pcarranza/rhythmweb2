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
    class Object(object):
        pass
    class GObject(object):
        pass

    @classmethod
    def property(*args, **kwargs):
        return mock.Mock()

class RB(object):
    class RhythmDBPropType(object):
        ENTRY_ID = 1
        TITLE = 2
        ARTIST = 3
        ALBUM = 4
        TRACK_NUMBER = 5
        DURATION = 6
        RATING = 7
        YEAR = 8
        GENRE = 9
        PLAY_COUNT = 10
        LOCATION = 11
        BITRATE = 12
        LAST_PLAYED = 13

class GLib(object):
    pass

class Peas(object):
    class Activatable(object):
        pass
" > gi/repository.py
touch gobject.py
touch gtk.py
