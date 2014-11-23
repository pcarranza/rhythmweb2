import socket

from time import time as timestamp
from rhythmweb.conf import Configuration
from contextlib import contextmanager

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

        with self.socket() as sock:
            sock.sendall(['{} {} {}'.format(name, value, int(timestamp()))])

    @contextmanager
    def socket(self):
        try:
            if not self.sock:
                self.sock = socket.socket()
                self.sock.connect((self.server, self.port))
            yield self.sock
        except socket.error:
            self.sock = None


def time(metric):
    def decorator(function):
        def wrap(*args, **kwargs):
            start = timestamp()
            value = function(*args, **kwargs)
            end = timestamp()
            metrics.record(metric, end - start)
            return value
        return wrap
    return decorator

metrics = Metrics() 
