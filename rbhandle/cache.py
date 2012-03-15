# -*- coding: utf-8 -
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

from serve.log.loggable import Loggable
from gi.repository import RB
import os.path, urllib

class CacheHandler(Loggable):
    
    __CACHE_ARTISTS = 'artists'
    __CACHE_GENRES = 'genres'
    __CACHE_ALBUMS = 'albums'
    __CACHE_MAX_ARTIST = 'max-artist'
    __CACHE_MAX_GENRE = 'max-genre'
    __CACHE_MAX_ALBUM = 'max-album'
    
    
    def __init__(self, shell):
        self.shell = shell
        
        self.__db_cache = {
                           self.__CACHE_ARTISTS : {},
                           self.__CACHE_MAX_ARTIST : None,
                           self.__CACHE_ALBUMS : {},
                           self.__CACHE_MAX_ALBUM : None,
                           self.__CACHE_GENRES : {},
                           self.__CACHE_MAX_GENRE : None
                           }
        
        self.__db_cache_loaded = False

    
    def __assert_cache(self):
        if not self.__db_cache_loaded:
            self.warning("Forcing cache load")
            self.__db.entry_foreach(self.__force_entry_load_into_cache)
            
            
    def __force_entry_load_into_cache(self, entry):
        self.__append_entry_to_cache(entry)
        
        
    def get_biggest_artist(self):
        '''
        Gets the artist that has more songs registered in the DB
        @return: a (name, value) tuple
        '''
        self.__assert_cache()
        max_artist = self.__db_cache[self.__CACHE_MAX_ARTIST]
        return (max_artist, self.__db_cache[self.__CACHE_ARTISTS][max_artist]) 
    
    
    def get_biggest_album(self):
        '''
        Gets the album that has more songs registered in the DB
        @return: a (name, value) tuple
        '''
        self.__assert_cache()
        max_album = self.__db_cache[self.__CACHE_MAX_ALBUM]
        return (max_album, self.__db_cache[self.__CACHE_ALBUMS][max_album])
    

    def get_biggest_genre(self):
        '''
        Gets the genre that has more songs registered in the DB
        @return: a (name, value) tuple
        '''
        self.__assert_cache()
        max_genre = self.__db_cache[self.__CACHE_MAX_GENRE]
        return (max_genre, self.__db_cache[self.__CACHE_GENRES][max_genre])
        
        
    def get_artists(self):
        '''
        Gets the artists cached dictionary
        '''
        self.__assert_cache()
        return self.__db_cache[self.__CACHE_ARTISTS]
    
    
    def get_albums(self):
        '''
        Gets the albums cached dictionary
        '''
        self.__assert_cache()
        return self.__db_cache[self.__CACHE_ALBUMS]
    
    
    def get_genres(self):
        '''
        Gets the genres cached dictionary
        '''
        self.__assert_cache()
        return self.__db_cache[self.__CACHE_GENRES]
        
        
    def __append_entry_to_cache(self, entry):
        '''
        Appends the given entry to the rbhandler cache 
        '''
        self.__db_cache_loaded = True
        
        entry_id = self.get_entry_id(entry)
        location = self.get_value(entry, RB.RhythmDBPropType.LOCATION)
        
        if location and str(location).startswith('file://'):
            fpath = urllib.url2pathname(location)
            fpath = str(fpath).replace('file://', '')
            if not os.path.exists(fpath):
                self.trace('Skipping missing file %s' % fpath)
                return

        artist = self.get_value(entry, RB.RhythmDBPropType.ARTIST)
        album = self.get_value(entry, RB.RhythmDBPropType.ALBUM)
        genre = self.get_value(entry, RB.RhythmDBPropType.GENRE)
        play_count = self.get_value(entry, RB.RhythmDBPropType.PLAY_COUNT)
        
        if not artist:
            self.trace('Empty artist for entry %d %s, skipping' % (entry_id, location))
            return
        
        if not album:
            self.trace('Empty album for entry %d %s, skipping' % (entry_id, location))
            return
        
        if not genre:
            self.trace('Empty genre for entry %d %s, skipping' % (entry_id, location))
            return

        if not play_count:
            play_count = 0
        
        self.__append_artist(artist, play_count)
        self.__append_album(album, play_count)
        self.__append_genre(genre, play_count)
    
    
    def __append_artist(self, artist, play_count):
        self.trace('Append playcount in %d to artist "%s"' % (play_count, artist))    
        artists_cache = self.__db_cache[self.__CACHE_ARTISTS]
        
        if artists_cache.has_key(artist):
            artists_cache[artist] += play_count
        else:
            artists_cache[artist] = play_count
            
        if self.__db_cache[self.__CACHE_MAX_ARTIST] is None:
            self.__db_cache[self.__CACHE_MAX_ARTIST] = artist
        elif artists_cache[artist] > artists_cache[self.__db_cache[self.__CACHE_MAX_ARTIST]]:
            self.__db_cache[self.__CACHE_MAX_ARTIST] = artist
            
    
    def __append_album(self, album, play_count):
        self.trace('Append playcount in %d to album "%s"' % (play_count, album))
        albums_cache = self.__db_cache[self.__CACHE_ALBUMS]
        
        if albums_cache.has_key(album):
            albums_cache[album] += play_count
        else:
            albums_cache[album] = play_count

        if self.__db_cache[self.__CACHE_MAX_ALBUM] is None:
            self.__db_cache[self.__CACHE_MAX_ALBUM] = album
        elif albums_cache[album] > albums_cache[self.__db_cache[self.__CACHE_MAX_ALBUM]]:
            self.__db_cache[self.__CACHE_MAX_ALBUM] = album


    def __append_genre(self, genre, play_count):
        self.trace('Append playcount in %d to genre "%s"' % (play_count, genre))
        genres_cache = self.__db_cache[self.__CACHE_GENRES]
    
        if genres_cache.has_key(genre):
            genres_cache[genre] += play_count
        else:
            genres_cache[genre] = play_count

        if self.__db_cache[self.__CACHE_MAX_GENRE] is None:
            self.__db_cache[self.__CACHE_MAX_GENRE] = genre
        elif genres_cache[genre] > genres_cache[self.__db_cache[self.__CACHE_MAX_GENRE]]:
            self.__db_cache[self.__CACHE_MAX_GENRE] = genre

