def get_song(entry):
    if not entry:
        return None
    song = {}
    song['id'] = entry.id
    song['artist'] = entry.artist
    song['album'] = entry.album
    song['track_number'] = entry.track_number
    song['title'] = entry.title
    song['duration'] = entry.duration
    song['rating'] = entry.rating
    song['year'] = entry.year
    song['genre'] = entry.genre
    song['play_count'] = entry.play_count
    song['bitrate'] = entry.bitrate
    song['last_played'] = entry.last_played
    song['location'] = entry.location
    return song

def get_playlist(playlist, entries=None):
    if not playlist:
        return None
    plst = {}
    plst['id'] = playlist.id
    plst['name'] = playlist.name
    plst['visibility'] = playlist.visibility
    plst['is_group'] = playlist.is_group
    plst['is_playing'] = playlist.is_playing
    plst['type'] = playlist.source_type
    if entries:
        plst['entries'] = entries
    return plst

def get_status(handler):
    status = {}
    status['playing'] = handler.get_playing_status()
    if status['playing']:
        playing_entry = handler.get_playing_entry()
        playing_entry = handler.load_entry(playing_entry)
        if playing_entry:
            status['playing_entry'] = get_song(playing_entry)
            status['playing_time'] = handler.get_playing_time()
    status['playing_order'] = handler.get_play_order()
    status['muted'] = handler.get_mute()
    status['volume'] = handler.get_volume()
    return status
