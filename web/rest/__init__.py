from serve.rest.json import JSon



class Song:
    
    @staticmethod
    def get_song_as_JSon(rbhandler, entry_id):
        entry = rbhandler.load_entry(entry_id)
        
        if entry is None:
            return None
        
        json = JSon('entry')
        json.put('id', entry_id)
        json.put('artist', entry.artist)
        json.put('album', entry.album)
        json.put('track_number', entry.track_number)
        json.put('title', entry.title)
        json.put('duration', entry.duration)
        json.put('rating', entry.rating)
        json.put('year', entry.year)
        json.put('genre', entry.genre)
        json.put('play_count', entry.play_count)
        json.put('bitrate', entry.bitrate)
        json.put('last_played', entry.last_played)
        json.put('location', entry.location)
        
        return json
