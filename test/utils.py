
class Stub(object):

    def __init__(self, key=None):
        self.key = key

    def __getattr__(self, name):
        if name == 'id' and self.key:
            return self.key
        return name
