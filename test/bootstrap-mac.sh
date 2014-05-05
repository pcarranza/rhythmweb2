#!/bin/bash

if [[ ! -f rhythmweb.plugin ]]; then
    echo "This script has to be called from the root folder"
    exit 1
fi
mkdir -p gi
touch gi/__init__.py
echo "
class GObject(object):
    class Object(object):
        pass
    class GObject(object):
        pass

    @classmethod
    def property(*args, **kwargs):
        pass

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
