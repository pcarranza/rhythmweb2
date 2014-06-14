import os
import io
from datetime import timedelta, datetime
from collections import defaultdict

import logging
log = logging.getLogger(__name__)

class ResourceHandler(object):

    def __init__(self, resource):
        log.debug('Creating ResourceHandler for resource %s' % resource)
        self.resource = resource
        self.extension = str(os.path.splitext(self.resource)[1]).lower()
        self.content_types = {
            '.css': ('text/css', 't'),
            '.htm': ('text/html', 't'),
            '.html': ('text/html', 't'),
            '.gif': ('image/gif', 'b'),
            '.png': ('image/png', 'b'),
            '.jpg': ('image/jpeg', 'b'),
            '.jpeg': ('image/jpeg', 'b'),
            '.ico': ('image/ico', 'b'),
            '.svg': ('image/svg+xml', 't'),
            '.js': ('application/x-javascript', 't'),
        }

    def handle(self, response, accept_gzip=False):
        log.debug('Handling resource %s' % self.resource)

        (content_type, open_as) = self.content_types.get(self.extension,
                ('text/plain', 't'))

        mtime = os.path.getmtime(self.resource)
        mtime = datetime.fromtimestamp(mtime)
        expiration = datetime.now() + timedelta(days=365)

        headers = [("Content-type", content_type), \
                    ('Cache-Control', 'public'), \
                    ('Last-Modified', mtime.ctime()), \
                    ('Expires', expiration.ctime())]

        open_mode = 'r%s' % open_as

        with open(self.resource, open_mode) as f:
            response('200 OK', headers)
            return f.read()


class ServerException(Exception):

    def __init__(self, code, message):
        self.code = int(code)
        self.message = message


class ClientError(ServerException):

    def __init__(self, message):
        super(ClientError, self).__init__(400, 'Bad request: {}'.format(message))
