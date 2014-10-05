[![Build Status](https://travis-ci.org/pcarranza/rhythmweb2.svg?branch=master)](https://travis-ci.org/pcarranza/rhythmweb)
[![Coverage Status](https://coveralls.io/repos/pcarranza/rhythmweb2/badge.png?branch=master)](https://coveralls.io/r/pcarranza/rhythmweb?branch=master)

# Rhythmweb

A web ui for controlling the player, searching the library and controlling the queue on rhythmbox

## A screenshot is worth more than a thousand words

![An old screenshot](https://bitbucket.org/jimcerberus/rhythmweb/wiki/img/play_queue.png)

## Status

A long forgotten project, which I did not needed for quite some time (3 years according to the last commit), now it is back an alive just because I need it back.

Surprisingly working ok on a linux mint gtk3 with RB3, only search, quick controlling and queueing songs.

## Roadmap

Basically this is what is in my head regarding this project:

* ~~Compatibility with python3~~
* ~~Add system level testing to ensure backwards compatibility on the front end.~~ (Manual but is something)
* ~~Remove all the multiple inheritance mess~~
* ~~Add a nice test coverage from the controllers layer before refactoring anything, not a fixed goal.~~
* ~~Remove home baked template handling, use bottle or any other "one file" templating engine that can be included in the code instead.~~
* ~~Simplify route handling, stop loading code dinamically, register routes with decorators and move current pages to a controller scheme~~
* ~~Recover playlist handling~~
* ~~Maintain compatibility with the front end.~~
* ~~Fix radio sources playing from the page~~
* ~~Refactor the web serving layer, one port only, interprocess communication using pipes or maybe a socket file, whatever is simpler.~~
* ~~Simplify configuration to "no configuration at all"~~
* ~~Recover ability to play radio~~ search by type radio and play :smile:
* ~~Recover source selection and handling (I miss using radio)~~
* ~~Refactor all the backend code for simplification (focusing on decoupling and single responsibility) -> Controllers~~
* ~~Recover the artits/genre cloud~~
* Refactor all the backend code for simplification -> rbhandler
* Fix some usability issues in the mobile skin

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
