# Rhythmweb - Rhythmbox web REST + Ajax environment for remote control
# Copyright (C) 2010  Pablo Carranza
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from serve.rest.json import JSon


class Song:
    
    @staticmethod
    def get_song_as_JSon(rbhandler, entry_id):
        entry = rbhandler.load_entry(entry_id)
        
        if entry is None:
            return None
        
        json = JSon()
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


class Playlist:
    
    @staticmethod
    def get_playlist_as_JSon(playlist, entries = None):
        json = JSon()
        json.put('id', playlist.index)
        json.put('name', playlist.name)
        json.put('visibility', playlist.visibility)
        json.put('is_group', playlist.is_group)
        json.put('is_playing', playlist.is_playing)
        if not entries is None:
            json.put('entries', entries)
        return json

    
class Status:
    
    @staticmethod
    def get_status_as_JSon(handler):
        is_playing = handler.get_playing_status()
        
        status = JSon()
        status.put('playing', is_playing)
        if is_playing:
            playing_entry_id = handler.get_playing_entry_id()
            if playing_entry_id:
                status.put('playing_entry', Song.get_song_as_JSon(handler, playing_entry_id))
                status.put('playing_time', handler.get_playing_time())
            
        status.put('playing_order', handler.get_play_order())
        status.put('muted', handler.get_mute())
        status.put('volume', handler.get_volume())
        
        return status
