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
from serve.log.loggable import Loggable
from SocketServer import TCPServer
import SocketServer
import threading
import socket
import sys
import time
import select

ERRORS = {
  400 : 'Bad request',
  405 : 'Method not allowed',
  500 : 'Internal server error',
  503 : 'Service Unavailable'
}


class BufferProxyServer(TCPServer, Loggable):
    
    def __init__(self, proxy_host, proxy_port, target_host, target_port):
        TCPServer.__init__(self, (proxy_host, proxy_port), SocketServer.StreamRequestHandler)
        self.target_address = (target_host, target_port)
        self.server_thread = None
        self.daemon_threads = False
        self.default_buffer_size = 1024
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False

       

    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.
        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """
        self.__is_shut_down.clear()
        try:
            while not self.__shutdown_request:
                try:
                    r, w, e = select.select([self], [], [], poll_interval)
                    if self in r:
                        self._handle_request_noblock()
                except Exception, e:
                    self.debug('Exception handling request: %s' % e)
        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()
    
    
    def shutdown(self):                                                                        
        self.__shutdown_request = True
        self.__is_shut_down.wait()
    
    
    def start(self):
        if not self.server_thread:
            self.debug('STARTING PROXY SERVER THREAD')
            self.server_thread = threading.Thread(target=self.serve_forever)
            self.server_thread.start()
            self.debug('PROXY SERVER THREAD STARTED')
        
        
    def stop(self):
        if self.server_thread:
            self.debug('STOPPING PROXY SERVER THREAD...')
            self.shutdown()
            self.debug('PROXY SERVER THREAD STOPPED')
            
        self.server_thread = None
        
        
    def clean_line(self, requestline):
        if requestline[-2:] == '\r\n':
            return requestline[:-2]
        elif requestline[-1:] == '\n':
            return requestline[:-1]
        return requestline


    def handle_request(self):
        self.trace('HANDLING REQUEST')
        return self._handle_request_noblock(self)
        
        
    def _handle_request_noblock(self):
        self.trace('HANDLING NON_BLOCKING REQUEST')
        
        try:
            request, client_address = self.socket.accept()
        except Exception, e:
            self.error('Request buffer handle exception: %s' % e)
            
        t = threading.Thread(target = self.process_request_thread,
                     args = (request, client_address))
        
        if self.daemon_threads:
            t.setDaemon (1)
            
        t.start()
        
        
    def process_request_thread(self, request, client_address):
        self.debug('Handling request with proxy from address %s' % client_address[0])
        
        buffer_size = self.default_buffer_size
        try:
            rfile = request.makefile('rb', buffer_size)
            try:
                buffer = self.read_request(rfile)
            except CommandNotSupportedError, e:
                return self.send_error(request, 405)
                
            self.trace('Closing request...')
            rfile.close()
            
            self.trace('Creating client socket')
            
            try:
                client = socket.socket()
                client.connect(self.target_address)
            except Exception, e:
                return self.send_error(request, 503, e)
            
            
            self.trace('Writing request in client socket')
            wfile = client.makefile('wb', buffer_size)
            try:
                wfile.writelines(buffer)
            except Exception, e:
                return self.send_error(request, 503, e)
            finally:
                self.trace('Closing client socket requests')
                wfile.close()
            
            
            wfile = request.makefile('wb', buffer_size)
            rfile = client.makefile('rw', buffer_size)
            self.trace('Reading client response and writing to the main response')
            
            try:
                while True:
                    try:
                        line = rfile.next()
                        wfile.write(line)
                    except StopIteration:
                        break
                    
                return True
            
            except Exception, e:
                self.error(e)
                
            finally:
                self.trace('Closing client response and request socket')
                rfile.close()
                wfile.close()
            
        except Exception, e:
            return self.send_error(request, 500, e)
        
        
    def send_error(self, request, code, message=None):
        if not ERRORS.has_key(code):
            error = 'Invalid error code %d' % code
            code = 500
        else:
            error = ERRORS[code]
            
        if not message is None:
            error = '%s %s' % (error, message)
            
        self.error(error)
        
        error = 'HTTP/1.1 %d %s' % (code, error)
        
        wfile = request.makefile('wb', self.default_buffer_size)
        wfile.writelines([error])
        wfile.close()
        return False
        
    def read_request(self, rfile):
        buffer = []
        command = None
        length = 0
        self.trace('Reading client request')
        while True:
            try:
                line = rfile.next()
                buffer.append(line)
                
                if command is None:
                    command = str(line).split(' ')[0]
                    if command not in ['GET', 'POST']:
                        raise CommandNotSupportedError('Command %s is not supported' % command)
                
                if length == 0: 
                    if line.startswith('Content-Length:'):
                        length = int(line.split(' ')[1])
                
                if not self.clean_line(line):
                    break
                
            except StopIteration:
                break
        
        if length > 0:
            self.trace('Reading Content...')
            buffer_size = 1024
            while True:
                try:
                    if buffer_size < length:
                        line = rfile.read(buffer_size)
                        length -= buffer_size
                    else:
                        line = rfile.read(length)
                        
                    buffer.append(line)
                    
                    if buffer_size > length:
                        break
                    
                except StopIteration:
                    break
        
        return buffer
    
    

class CommandNotSupportedError(RuntimeError):
    pass


def __debug(message):
    
    sys.stdout.write(message)
    if not str(message).endswith('\n'):
        sys.stdout.write('\n')


if __name__ == '__main__':
    bs = BufferProxyServer('0.0.0.0', 7001, 7000)
    bs.debug = __debug
    bs.trace = __debug
    bs.info = __debug
    bs.error = __debug
    bs.start()
    while True:
        sys.stdout.write('Waiting connections...\n')
        time.sleep(50)
    