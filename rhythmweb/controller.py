
from collections import defaultdict

from rhythmweb.model import get_song

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
