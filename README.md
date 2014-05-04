# Rhythmweb

A web ui for controlling the player, searching the library and controlling the queue on rhythmbox

## A screenshot is worth more than a thousand words

![An old screenshot](https://bitbucket.org/jimcerberus/rhythmweb/wiki/img/play_queue.png)

## Status

A long forgotten project, which I did not needed for quite some time (3 years according to the last commit), now it is back an alive just because I need it back.

Surprisingly working ok on a linux mint gtk3 with RB3, only search, quick controlling and queueing songs.

### Some notes on the instalation process:

From GTK3 the actual folder to install the project is ~/.local/share/rhythmbox/plugins/rhythmweb
The rest is pretty much the same.

Also the default configuration looks a bit wrong, it should be something like this:

    ...
    hostname=127.0.0.1
    port=7001

    proxy=True
    proxy.port=7000
    proxy.hostname=0.0.0.0
    ...

### What is there to come

A lot of love that this project did not had for a long time. I learned a lot of better python coding in this time, so it is time to move it back to TDD (creating tests for legacy code is quite an experience) and bring back the missing features, as more stability and better interprocess comunication (and better explanations on the why)
