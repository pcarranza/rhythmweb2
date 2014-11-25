
from collections import defaultdict

from rhythmweb.model import get_song, get_playlist
from rhythmweb.rb import RBHandler, RBEntry
from rhythmweb import metrics

import logging
log = logging.getLogger(__name__)

rb_handler = {}

def set_shell(shell):
    rb_handler['rb'] = RBHandler(shell)

def get_handler():
    return rb_handler.get('rb', None)

class Song(object):

    def __init__(self):
        self.rb = get_handler()

    @metrics.time('controller.song.find_by_id')
    def find_by_id(self, song_id):
        entry = self.rb.get_entry(song_id)
        if not entry:
            return None
        log.debug('Found song %d', song_id)
        return get_song(entry)

    @metrics.time('controller.song.rate')
    def rate(self, song):
        self.set_rating(song, song['rating'])

    @metrics.time('controller.song.set_rate')
    def set_rating(self, song, rating):
        song_id = song['id']
        self.rb.set_rating(song_id, rating)
        song['rating'] = rating
        log.debug('Song %d rated as %d', song_id, rating)


class Queue(object):

    def __init__(self):
        self.rb = get_handler()

    @metrics.time('controller.queue.get')
    def get_queue(self):
        entries = self.rb.get_play_queue()
        queue = defaultdict(lambda:[])
        for entry in entries:
            queue['entries'].append(get_song(entry))
        return queue

    @metrics.time('controller.queue.enqueue')
    def enqueue(self, entry_id):
        self.rb.enqueue(as_list(entry_id))

    @metrics.time('controller.queue.dequeue')
    def dequeue(self, entry_id):
        self.rb.dequeue(as_list(entry_id))

    @metrics.time('controller.queue.shuffle')
    def shuffle_queue(self):
        self.rb.shuffle_queue()

    @metrics.time('controller.queue.clear')
    def clear_queue(self):
        self.rb.clear_play_queue()


class Player(object):

    def __init__(self):
        self.rb = get_handler()

    @metrics.time('controller.player.next')
    def next(self):
        self.rb.play_next()

    @metrics.time('controller.player.previous')
    def previous(self):
        self.rb.previous()

    @metrics.time('controller.player.play_pause')
    def play_pause(self):
        self.rb.play_pause()

    @metrics.time('controller.player.seek')
    def seek(self, time=0):
        self.rb.seek(time)

    @metrics.time('controller.player.play_entry')
    def play_entry(self, entry_id=None):
        self.rb.play_entry(entry_id)

    @metrics.time('controller.player.mute')
    def mute(self):
        self.rb.toggle_mute()

    @metrics.time('controller.player.set_volume')
    def set_volume(self, volume=1.0):
        self.rb.set_volume(volume)

    @metrics.time('controller.player.status')
    def status(self):
        status = {}
        handler = self.rb
        status['playing'] = handler.get_playing_status()
        if status['playing']:
            playing_entry = handler.get_playing_entry()
            if playing_entry:
                status['playing_entry'] = get_song(playing_entry)
                status['playing_time'] = handler.get_playing_time()
        status['playing_order'] = handler.get_play_order()
        status['muted'] = handler.get_mute()
        status['volume'] = handler.get_volume()
        return status


@metrics.time('controller.query_library')
def query_library(what):
    log.debug('Looking for library %s', what)
    return getattr(get_handler().library, what, {})


class Query(object):

    def __init__(self):
        self.rb = get_handler()

    @metrics.time('controller.query.query')
    def query(self, query_filter):
        entries = defaultdict(lambda: [])
        for entry in self.rb.query(query_filter):
            entries['entries'].append(get_song(entry))
        return entries


class Source(object):

    def __init__(self):
        self.rb = get_handler()

    @metrics.time('controller.source.get_sources')
    def get_sources(self):
        return self.rb.get_playlists()

    @metrics.time('controller.source.get')
    def get_source(self, source_id):
        sources = self.rb.get_playlists()
        source = sources[source_id] if sources else None
        if source:
            self.rb.load_source_entries(source)
        return source

    @metrics.time('controller.source.enqueue')
    def enqueue_by_id(self, source_id):
        playlist = self.get_source(source_id) 
        if not playlist:
            return None
        return self.rb.enqueue_source(playlist)

    @metrics.time('controller.source.play')
    def play_source(self, source_id):
        source = self.get_source(source_id)
        if not source:
            return False
        return self.rb.play_source(source)

    @metrics.time('controller.source.get_playlist')
    def get_playlist(self, playlist_id):
        return get_playlist(self.get_source(playlist_id))

    @metrics.time('controller.source.get_playlists')
    def get_playlists(self):
        return [get_playlist(source) for source in self.get_sources()]


def as_list(value):
    value = [value] if not isinstance(value, list) else value
    return value
