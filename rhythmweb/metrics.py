import socket
import logging

from socket import error as SocketError

from time import time as timestamp
from rhythmweb.conf import Configuration
from contextlib import contextmanager

log = logging.getLogger(__name__)


class Metrics(object):

    def __init__(self):
        conf = Configuration.get_instance()
        self.enabled = conf.get_boolean('metrics.enabled')
        self.server = conf.get_string('metrics.server')
        self.port = conf.get_int('metrics.port')
        self.sock = None

    def record(self, name, value):
        if not self.enabled:
            return
        if self.connect():
            try:
                self.sock.sendall(['rhythmweb.{} {} {}'.format(
                    name, value, int(timestamp()))])
            except SocketError as e:
                log.exception('Could not send metrics %s: %s', name, e)

    def connect(self):
        if not self.sock:
            try:
                log.debug('Opening metrics socket on %s:%d', self.server, self.port)
                self.sock = socket.socket()
                self.sock.connect((self.server, self.port))
            except SocketError as e:
                log.exception('Could not open metrics socket %s', e)
                self.sock = None
                return False
        return True


def time(metric):
    def decorator(function):
        def wrap(*args, **kwargs):
            start = timestamp()
            value = function(*args, **kwargs)
            end = timestamp()
            metrics.record(metric, int((end - start) * 1000))
            return value
        return wrap
    return decorator

metrics = Metrics() 
