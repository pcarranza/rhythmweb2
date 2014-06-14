from web.rest import RBRest
from rbhandle.query import InvalidQueryException
from serve.request import ServerException, ClientError
from rhythmweb.model import get_song
from rhythmweb.controller import Query

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
        query_filter = self.get_query_filter()
        query = Query()
        try:
            return query.query(query_filter)
        except InvalidQueryException as e:
            log.error('Invalid query {}'.format(query_filter))
            raise ClientError(e.message)
        except Exception as e:
            log.exception(e)
            raise ServerException(500, 'Exception when executing query: %s' % e)

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
