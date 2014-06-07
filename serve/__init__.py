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


from gi.repository import GObject
from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import make_server

from serve.proxy import BufferProxyServer

import logging
log = logging.getLogger(__name__)

class CGIServer(object):


    def __init__(self, application, config):
        if not config:
            raise ValueError("Configuration is required")
        if not application:
            raise ValueError("Application is required")
        self._config = config
        self._application = application
        self._internal_server = None
        self._running = False
        self._proxy_server = None

    def start(self):
        log.info('   STARTING SERVER')
        config = self._config
        hostname = config.get_string('hostname')
        port = config.get_int('port')
        log.info('   HOSTNAME   %s' % hostname)
        log.info('   PORT       %d' % port)

        use_proxy = config.get_boolean('proxy')
        proxy_port = config.get_int('proxy.port')
        proxy_hostname = config.get_string('proxy.hostname')

        if self._internal_server is None:
            self._internal_server = make_server(
                hostname,
                port,
                self._application.handle_request,
                handler_class=WSGIRequestHandler)

        self._watch_id = GObject.io_add_watch(
            self._internal_server.socket,
            GObject.IO_IN,
            self._idle_request_loop)

        self._running = True
        log.info('   SERVER STARTED')

        if use_proxy == True:
            log.info('   PROXY_HOSTNAME %s' % proxy_hostname)
            log.info('   PROXY_PORT     %d' % proxy_port)

            log.info('   STARTING PROXY')
            self._proxy_server = BufferProxyServer(proxy_hostname,
                proxy_port, hostname, port)
            self._proxy_server.start()
            log.info('   PROXY STARTED')

    def stop(self):
        log.info('   STOPPING SERVER')
        GObject.source_remove(self._watch_id)
        if self._internal_server is None:
            return

        if not self._proxy_server is None:
            log.info('   STOPPING PROXY SERVER')
            self._proxy_server.stop()

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
