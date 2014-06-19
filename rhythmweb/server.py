import re
import cgi

from rhythmweb.view import app

import logging
log = logging.getLogger(__name__)

app.mount('./resources/default', 'default', ignore='/resources/default')
app.mount('./resources/touch', 'mobile', ignore='/resources/touch')

match_mobile = re.compile(r'(Android|iPhone)')

class Server(object):

    def __init__(self, rb):
        self.rb = rb

    def handle_request(self, environ, response):
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/index.html')
        group = 'mobile' if match_mobile.match(environ.get('HTTP_USER_AGENT', '')) else 'default'
        try:
            if method == 'GET':
                content = app.get_file(path, group)
                if content:
                    response.reply_with_file(content)
                content = app.route(path)
                if content is None:
                    response.reply_with_not_found()
                response.reply_with_json(content)

            if method == 'POST':
                post = self.parse_post_parameters(environ)
                content = app.route(path, **post)
                if content is None:
                    response.reply_with_not_found()
                response.reply_with_json(content)

        except ServerError as e:
            response.reply_with_server_error(e)

    def parse_post_parameters(self, environ):
        parsed = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values=True
        )
        post = {}
        for key in parsed.keys():
            post[key] = parsed[key].value
        return post


class ServerError(Exception):
    pass
