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


from serve.rest import JSon
from serve.request import ServerException

import logging
log = logging.getLogger(__name__)

class BaseRest(object):

    __environ = None
    __parameters = None
    __path_params = None
    __components = None

    def __init__(self, components):
        self.__components = components

    def __do_headers(self, headers=[]):
        if not headers:
            headers.append(('Content-type','text/html; charset=UTF-8'))

        return headers

    def do_get(self, environ, response):
        self.__environ = environ
        self.parse_path_parameters()

        try:
            return_value = self.get()
            log.debug('GET Method executed OK, sending ok response')
            return self.__return_ok(return_value, response)

        except ServerException as e:
            log.error('ServerException handling rest get', exc_info=True)
            response('%d %s' % (e.code, e.message), self.__do_headers())
            return e.message

        except Exception as e:
            log.error('Unknown exception when executing GET method: %s' % e, exc_info=True)
            response('%d %s' % (500, e), self.__do_headers())
            return '%d %s' % (500, e)


    def do_post(self, environ, post_params, response):
        self.__parameters = post_params
        self.__environ = environ
        self.parse_path_parameters()

        log.debug("post parameters {}".format(post_params))

        try:
            return_value = self.post()
            log.debug('POST Method executed OK, sending ok response')
            return self.__return_ok(return_value, response)

        except ServerException as e:
            log.error('ServerException handling rest get', exc_info=True)
            response('%d %s' % (e.code, e.message), self.__do_headers())
            return e.message

        except Exception as e:
            log.error('Unknown exception when executing GET method: %s' % e, exc_info=True)
            response('%d %s' % (500, e), self.__do_headers())
            return '%d %s' % (500, e)

    def __return_ok(self, value, response):
        try:
            if value is None:
                return self.__do_page_not_found(response)

            if isinstance(value, JSon):
                headers = []
                headers.append(('Content-type','application/json; charset=UTF-8'))
                headers.append(('Cache-Control: ', 'no-cache; must-revalidate'))
                json = value.parse()
                response('200 OK', self.__do_headers(headers))
                log.debug('Returning JSON: %s' % json)
                return json

            response('200 OK', self.__do_headers())
            return str(value)
        except:
            log.error('Exception sending OK Value: "%s"' % value, exc_info=True)
            return None

    def parse_path_parameters(self):
        path_params = self.__environ['PATH_PARAMS']

        querystring_params = []
        if path_params:
            params = str(path_params).split('/')
            for param in params:
                if param:
                    querystring_params.append(param)

        self.__path_params = querystring_params

    def __do_page_not_found(self, response):
        response('404 NOT FOUND', self.__do_headers())
        return self.__not_found()

    def __not_found(self):
        return 'Page not found'

    def get(self):
        raise ServerException(405, 'method GET not allowed')

    def post(self):
        raise ServerException(405, 'method POST not allowed')

    def unpack_value(self, value):
        if type(value) is dict:
            log.debug('Value is as dictionary, returning dictionary')
            return value

        elif type(value) is list:
            if len(value) == 1:
                log.debug('Value was packed as 1 element list')
                svalue = value[0]
                if type(svalue) is str:
                    svalue = svalue.strip()
                    log.debug('Value "%s" is a string, returning stripped' % svalue)
                else:
                    log.debug('Value has type "%s", returning value' % type(svalue))

                return svalue

            else:
                log.debug('Value is a list of %d elements, returning list' % len(value))
                return value

        else:
            log.debug('Value has type "%s", returning value' % type(value))
            return value

    def pack_as_list(self, value):
        if type(value) is list:
            return value
        elif type(value) is dict:
            return_value = []
            for v in value:
                return_value.append(value[v])
            return return_value
        elif type(value) is str and ',' in value:
            return value.split(',')
        else:
            return [value]

    def get_component(self, key):
        log.debug('Obtaining component %s' % key)

        if not self.__components:
            raise Exception('No components are loaded')

        if key not in self.__components:
            raise Exception('Components dictionary does not contains key "%s"' % key)

        return self.__components[key]

    def get_environment(self):
        return self.__environ

    def get_parameters(self):
        return self.__parameters

    def get_path_parameters(self):
        return self.__path_params

    def has_parameter(self, key):
        if not self.__parameters:
            return False

        return key in self.__parameters

    def get_parameter(self, key, required=False):
        if not self.has_parameter(key):
            if required:
                raise ServerException(400, 'Bad request, no "%s" parameter' % key)
            else:
                return None

        try:
            param = self.__parameters[key]
            param = self.unpack_value(param)
            return param
        except:
            raise ServerException(500, 'Could not unpack post parameter %d' % key)

    def has_post_parameters(self):
        if self.__parameters is None:
            return False

        if not self.__parameters:
            return False

        if len(self.__parameters) == 0:
            return False

        return True

    def has_path_parameters(self):
        if self.__path_params is None:
            return False

        if not self.__path_params:
            return False

        if len(self.__path_params) == 0:
            return False
        return True

    def get_parameters_size(self):
        if not self.__parameters:
            return 0

        return len(self.__parameters)

    def get_path_parameters_size(self):
        if not self.__path_params:
            return 0

        return len(self.__path_params)

    def get_path_parameter(self, index):
        if not self.__path_params:
            log.warn('No path param with index %d (empty path params)' % index)
            return None

        if self.get_path_parameters_size() < index + 1:
            log.warn('No path param with index %d' % index)
            return None

        try:
            param = self.__path_params[index]
            param = self.unpack_value(param)
            return param
        except:
            raise ServerException(500, 'Could not unpack path parameter %d' % index)


class RBRest(BaseRest):

    def get_rb_handler(self):
        return self.get_component('RB')

    def get_song_as_json(self, entry):
        log.debug('Obtaining entry %s as json object' % entry)
        return Song.get_song_as_JSon(entry)

    def get_songs_as_json_list(self, entries):
        log.debug('Loading entries list as json list')
        entries_list = []
        for entry in entries:
            entry = self.get_song_as_json(entry)
            entries_list.append(entry)

        return entries_list

    def get_source_as_json(self, playlist, entries = None):
        log.debug('Loading playlist as json object')
        return Playlist.get_source_as_JSon(playlist, entries)

    def get_status_as_json(self):
        log.debug('Loading status as json object')
        return Status.get_status_as_JSon(self.get_rb_handler())

    def get_library_as_json_list(self, library):
        log.debug('Converting library dictionary to json list')
        libraries = []

        for key in library:
            libraries.append(self.get_name_value_as_json(key, library[key]))

        return libraries

    def get_name_value_as_json(self, name, value):
        json = JSon()
        json.put('name', name)
        json.put('value', value)
        return json


class Song:

    @staticmethod
    def get_song_as_JSon(entry):
        if entry is None:
            return None

        json = JSon()
        json.put('id', entry.id)
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
    def get_source_as_JSon(playlist, entries = None):
        json = JSon()
        json.put('id', playlist.id)
        json.put('name', playlist.name)
        json.put('visibility', playlist.visibility)
        json.put('is_group', playlist.is_group)
        json.put('is_playing', playlist.is_playing)
        json.put('type', playlist.source_type)
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
            playing_entry = handler.get_playing_entry()
            playing_entry = handler.load_entry(playing_entry)
            if playing_entry:
                status.put('playing_entry', Song.get_song_as_JSon(playing_entry))
                status.put('playing_time', handler.get_playing_time())

        status.put('playing_order', handler.get_play_order())
        status.put('muted', handler.get_mute())
        status.put('volume', handler.get_volume())

        return status
