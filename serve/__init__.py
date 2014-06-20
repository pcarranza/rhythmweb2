from gi.repository import GObject
from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import make_server

from serve.proxy import BufferProxyServer

import logging
log = logging.getLogger(__name__)

class CGIServer(object):

    def __init__(self, application):
        if not application:
            raise ValueError("Application is required")
        if not application.config:
            raise ValueError("Configuration is required")
        self._application = application
        self._internal_server = None
        self._running = False
        self._proxy_server = None
        self._watch_id = None

    def start(self):
        log.info('   STARTING SERVER')
        config = self._application.config
        hostname = config.get_string('hostname')
        port = config.get_int('port')
        log.info('   HOSTNAME   %s' % hostname)
        log.info('   PORT       %d' % port)

        use_proxy = config.get_boolean('proxy')
        proxy_port = config.get_int('proxy.port')
        proxy_hostname = config.get_string('proxy.hostname')

        self._internal_server = make_server(
            hostname,
            port,
            self._application.handle_request,
            handler_class=WSGIRequestHandler)

        self._watch_id = GObject.io_add_watch(
            self._internal_server.socket,
            GObject.IO_IN,
            self._idle_request_loop)

        if use_proxy == True:
            log.info('   PROXY_HOSTNAME %s' % proxy_hostname)
            log.info('   PROXY_PORT     %d' % proxy_port)

            log.info('   STARTING PROXY')
            self._proxy_server = BufferProxyServer(proxy_hostname,
                proxy_port, hostname, port)
            self._proxy_server.start()
            log.info('   PROXY STARTED')

        self._running = True
        log.info('   CGI SERVER STARTED')

    def stop(self):
        if self._proxy_server:
            log.info('   STOPPING PROXY SERVER')
            self._proxy_server.stop()

        if self._internal_server:
            log.info('   STOPPING CGI SERVER')
            GObject.source_remove(self._watch_id)
            self._internal_server.server_close()
        self._internal_server = None
        self._proxy_server = None
        self._running = False
        log.info('   SERVER STOPPED')

    def _idle_request_loop(self, source, cb_condition):
        log.debug('Handling request')
        if not self._running:
            log.debug('NOT RUNNING')
            return False
        self._internal_server.handle_request()
        return True
