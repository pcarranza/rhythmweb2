from serve.server import HttpServer
from serve.conf.config import Configuration


def runserver():
    config = Configuration.instance()
    config._params={'port' : '8001', \
                    'log.file' : '/home/jim/rb-serve.log', \
                    'bind' : '0.0.0.0' }
    if Configuration.instance().getBoolean('debug'):
        Configuration.instance().printConfiguration()
    ns = HttpServer()
    ns.start()
    
    ns.join(timeout=10)
    
    ns.stop()
    print "Server is closed"


if __name__ == "__main__":
    runserver()
    