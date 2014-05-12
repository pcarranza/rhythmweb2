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


from serve.request import ServerException
from web.rest import RBRest

import logging
log = logging.getLogger(__name__)

class Page(RBRest):

    def get(self):
        song_id = self.get_song_id()

        if song_id is None:
            return None

        return self.get_song_as_json(song_id)

    def post(self):
        song_id = self.get_song_id()

        if song_id is None:
            return None

        if self.has_parameter('rating'):
            rating = self.get_parameter('rating')
            try:
                rating = int(rating)
            except:
                raise ServerException(400, 'Bad Request: rating must be a number')

            log.info('Setting Rating %s for song "%s"' % (rating, song_id))
            self.get_rb_handler().set_rating(song_id, rating)

        return self.get()

    def __not_found(self):
        return 'Song %s not found :(' % self.get_song_id()

    def get_song_id(self):
        log.debug('Getting song id from path parameters')

        if not self.has_path_parameters():
            return None

        if self.get_path_parameters_size() != 1:
            raise ServerException(400, 'Bad Request: no song id in path')
        log.debug('Reading path parameters index 0')
        song_id = self.get_path_parameter(0)
        try:
            song_id = int(song_id)
        except:
            raise ServerException(400, 'Bad Request: song id is not a number')

        return song_id
