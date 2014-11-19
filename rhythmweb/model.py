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

def get_playlist(playlist):
    if not playlist:
        return None
    plst = {}
    plst['id'] = playlist.id
    plst['name'] = playlist.name
    plst['type'] = playlist.source_type
    if playlist.entries:
        plst['entries'] = [get_song(entry) for entry in playlist.entries]
    else:
        plst['entries'] = []
    return plst
