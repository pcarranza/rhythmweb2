
from collections import defaultdict

from rhythmweb.model import get_song, get_status

import logging
log = logging.getLogger(__name__)

class Song(object):

    def __init__(self, rb):
        self.rb = rb

    def find_by_id(self, song_id):
        entry = self.rb.get_entry(song_id)
        if not entry:
            return None
        entry = self.rb.load_entry(entry)
        log.debug('Found song %d', song_id)
        return get_song(entry)

    def rate(self, song):
        song_id = song['id']
        rating = song['rating']
        self.rb.set_rating(song_id, rating)
        log.debug('Song %d rated as %d', song_id, rating)


class Queue(object):

    def __init__(self, rb):
        self.rb = rb

    def get_queue(self):
        entries = self.rb.get_play_queue()
        queue = defaultdict(lambda:[])
        for entry in entries:
            queue['entries'].append(get_song(entry))
        return queue

    def enqueue(self, entry_id):
        self.rb.enqueue(as_list(entry_id))

    def dequeue(self, entry_id):
        self.rb.dequeue(as_list(entry_id))

    def shuffle_queue(self):
        self.rb.shuffle_queue()

    def clear_queue(self):
        self.rb.clear_play_queue()


class Player(object):

    def __init__(self, rb):
        self.rb = rb

    def next(self):
        self.rb.play_next()

    def previous(self):
        self.rb.previous()

    def play_pause(self):
        self.rb.play_pause()

    def seek(self, time=0):
        self.rb.seek(time)

    def play_entry(self, entry_id=None):
        self.rb.play_entry(entry_id)

    def mute(self):
        self.rb.toggle_mute()

    def set_volume(self, volume=1.0):
        self.rb.set_volume(volume)

    def status(self):
        return get_status(self.rb)


class Query(object):

    def __init__(self, rb):
        self.rb = rb

    def query(self, query_filter):
        entries = defaultdict(lambda: [])
        for entry in self.rb.query(query_filter):
            entries['entries'].append(get_song(entry))
        return entries


class Source(object):

    def __init__(self, rb):
        self.rb = rb

    def get_sources(self):
        return self.rb.get_playlists()

    def get_source(self, source_id):
        sources = self.rb.get_playlists()
        return sources[source_id] if sources else None

    def enqueue_by_id(self, source_id):
        playlist = self.get_source(source_id) 
        if not playlist:
            return None
        return self.rb.enqueue_source(playlist)

    def play_source(self, source_id):
        source = self.get_source(source_id)
        if not source:
            return False
        return self.rb.play_source(source)



def as_list(value):
    value = [value] if not isinstance(value, list) else value
    return value
