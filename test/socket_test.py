import unittest
import hashlib
import threading

class TestSocketTalk(unittest.TestCase):

    def test_open_socket(self):
        server = RhythmboxServer()
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()
        client = RhythmboxClient(server.server_address)
        message = client.communicate('hola'.encode('UTF-8'))
        self.assertEquals('4d186321c1a7f0f354b297e8914ab240', message.decode('UTF-8'))
        server.shutdown()
 

import socket
import socketserver
import tempfile
from io import BytesIO

class RhythmboxClient(object):

    def __init__(self, address):
        self.address = address

    def communicate(self, message):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.address)
        received = BytesIO()
        try:
            sock.sendall(message)
            bytesbuffer = sock.recv(1024)
            while bytesbuffer:
                received.write(bytesbuffer)
                bytesbuffer = sock.recv(1024)
        finally:
            sock.close()
        return received.getvalue()

class RhythmboxServer(socketserver.UnixStreamServer):

    def __init__(self):
        self.allow_reuse_address = True
        self.request_queue_size = 10
        super(RhythmboxServer, self).__init__(
                tempfile.mktemp(prefix='rhythmbox', suffix='.sock'), 
                RhythmboxRequestHandler, True)

    def handle_grequest(self, fd, condition, callback):
        return self.handle_request()


class RhythmboxRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):
        req = self.request.recv(1024)
        md5 = hashlib.md5(req)
        self.wfile.write(md5.hexdigest().encode('UTF-8'))
        self.wfile.close()


