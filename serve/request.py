import os
import io
from datetime import timedelta, datetime

import logging
log = logging.getLogger(__name__)

class ResourceHandler(object):

    __content_type = None
    __open_as = None
    __file = None
    __extension = None

    def __init__(self, resource, content_type=None, open_as=''):
        try:
            log.debug('Creating ResourceHandler Instance for resource %s' % resource)

            self._content_type = content_type
            self.__open_as = open_as

            self.__file = resource
            self.__extension = str(os.path.splitext(self.__file)[1]).lower()

            log.debug('Resource %s file is %s' % (resource, self.__file))
        except:
            log.error('Exception initializing resource handler')

    def handle(self, response, accept_gzip=False):
        try:
            log.debug('Handling resource %s' % self.__file)

            (content_type, open_as) = self.__get_content_type()

            mtime = os.path.getmtime(self.__file)
            mtime = datetime.fromtimestamp(mtime)
            expiration = datetime.now() + timedelta(days=365)

            headers = [("Content-type", content_type), \
                       ('Cache-Control', 'public'), \
                       ('Last-Modified', mtime.ctime()), \
                       ('Expires', expiration.ctime())]

            open_mode = 'r%s' % open_as

            with open(self.__file, open_mode) as f:
                response('200 OK', headers)
                return f.read()
        except:
            log.error('Exception handling resource {}'.format(self.__file), exc_info=True)
            return ''

    def __get_content_type(self):
        if not self.__content_type:
            (self.__content_type, self.__open_as) = self.__content_type_by_ext(self.__extension)

        log.debug('Returning content type %s' % self.__content_type)
        return (self.__content_type, self.__open_as)

    def __content_type_by_ext(self, ext):
        if ext == '.css':
            return ('text/css', 't')
        if ext == '.htm':
            return ('text/html', 't')
        if ext == '.html':
            return ('text/html', 't')
        if ext == '.gif':
            return ('image/gif', 'b')
        if ext == '.png':
            return ('image/png', 'b')
        if ext == '.jpg':
            return ('image/jpeg', 'b')
        if ext == '.jpeg':
            return ('image/jpeg', 'b')
        if ext == '.ico':
            return ('image/ico', 'b')
        if ext == '.svg':
            return ('image/svg+xml', 't')
        if ext == '.js':
            return ('application/x-javascript', 't')

        return ('text/plain', 't')


class ServerException(Exception):

    def __init__(self, code, message):
        self.code = int(code)
        self.message = message


class ClientError(ServerException):

    def __init__(self, message):
        super(ClientError, self).__init__(400, 'Bad request: {}'.format(message))
