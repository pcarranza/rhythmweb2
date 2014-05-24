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
from web.rest import RBRest
from rbhandle.query import InvalidQueryException
from serve.request import ServerException

import logging
log = logging.getLogger(__name__)

class Page(RBRest):

    TYPES = {'song' : 'song',
             'radio' : 'iradio',
             'iradio' : 'iradio',
             'podcast' : 'podcast-post',
             'podcast-post' : 'podcast-post'}

    def get(self):
        log.info('GET search')
        handler = self.get_rb_handler()
        query_filter = self.get_query_filter()

        try:
            entries = handler.query(query_filter)
        except InvalidQueryException as e:
            raise ServerException(400, 'bad request: %s' % e.message)
        except Exception as e:
            raise ServerException(500, 'Exception when executing query: %s' % e)

        json = JSon()
        if entries:
            entries = self.get_songs_as_json_list(entries)
            json.put('entries', entries)
        else:
            log.info('empty result for query {}'.format(query_filter))

        return json

    def post(self):
        log.debug('POST search')
        return self.get()

    def get_query_filter(self):
        log.debug('get_query_filter')
        query_filter = {}

        if self.has_path_parameters():
            log.debug('Reading path parameters')
            query_filter = self.__unpack_path_params(self.get_path_parameters())
        else:
            log.debug('No search path parameters')

        if self.has_post_parameters():

            log.debug('Reading POST parameters')

            if not 'type' in query_filter and self.has_parameter('type'):
                query_filter['type'] = self.__unpack_type(self.get_parameter('type'))

            if self.has_parameter('artist'):
                query_filter['artist'] = self.get_parameter('artist')

            if self.has_parameter('title'):
                query_filter['title'] = self.get_parameter('title')

            if self.has_parameter('album'):
                query_filter['album'] = self.get_parameter('album')

            if self.has_parameter('rating'):
                rating = self.get_parameter('rating')

                if rating.isdigit():
                    irating = int(rating)
                else:
                    irating = len(str(rating).strip())

                query_filter['rating'] = irating

            if self.has_parameter('genre'):
                query_filter['genre'] = self.get_parameter('genre')

            if self.has_parameter('first'):
                query_filter['first'] = self.get_parameter('first')

            if self.has_parameter('limit'):
                query_filter['limit'] = self.get_parameter('limit')

            if self.has_parameter('all'):
                query_filter['all'] = self.get_parameter('all')
        else:
            log.debug('No search POST parameters')
        return query_filter

    def __unpack_type(self, type):
        if type in self.TYPES:
            log.debug('Returning type for "%s"' % type)
            return self.TYPES[type]

        log.debug('No type for "%s"' % type)
        return None

    def __unpack_path_params(self, path_params):
        unpacked = {}
        if type(path_params) is list:
            for index in range(len(path_params)):
                param = path_params[index]
                if param in self.TYPES:
                    unpacked['type'] = self.__unpack_type(param)

                elif 'limit' == param and len(path_params) > index + 1:
                    unpacked['limit'] = path_params[index + 1]

                elif 'first' == param and len(path_params) > index + 1:
                    unpacked['first'] = path_params[index + 1]

        elif path_params in self.TYPES:
            unpacked['type'] = self.__unpack_type(path_params)

        return unpacked
