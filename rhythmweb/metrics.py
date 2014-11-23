from time import time as timestamp
from rhythmweb.conf import Configuration

class Metrics(object):

    def __init__(self):
        conf = Configuration.get_instance()
        self.enabled = conf.get_boolean('metrics.enabled')
        self.server = conf.get_string('metrics.server')
        self.port = conf.get_int('metrics.port')

    def record(name, value):
        pass


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
