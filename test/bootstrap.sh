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
    pass

class GLib(object):
    pass

class Peas(object):
    class Activatable(object):
        pass
" > gi/repository.py
touch gobject.py
touch gtk.py
