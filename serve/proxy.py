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

from socketserver import TCPServer
import socketserver
import threading
import socket
import sys
import time
import select

import logging
log = logging.getLogger(__name__)

ERRORS = {
  400 : 'Bad request',
  405 : 'Method not allowed',
  500 : 'Internal server error',
  503 : 'Service Unavailable'
}


class BufferProxyServer(TCPServer):
    
    def __init__(self, proxy_host, proxy_port, target_host, target_port):
        TCPServer.__init__(self, (proxy_host, proxy_port), socketserver.StreamRequestHandler)
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
                except Exception as e:
                    log.error('Exception handling request: %s' % e, exc_info=True)
        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()
    
    
    def shutdown(self):                                                                        
        self.__shutdown_request = True
        self.__is_shut_down.wait()
    
    
    def start(self):
        if not self.server_thread:
            log.debug('STARTING PROXY SERVER THREAD')
            self.server_thread = threading.Thread(target=self.serve_forever)
            self.server_thread.start()
            log.debug('PROXY SERVER THREAD STARTED')
        
        
    def stop(self):
        if self.server_thread:
            log.debug('STOPPING PROXY SERVER THREAD...')
            self.shutdown()
            log.debug('PROXY SERVER THREAD STOPPED')
            
        self.server_thread = None
        
        
    def clean_line(self, requestline):
        if requestline[-2:] == '\r\n':
            return requestline[:-2]
        elif requestline[-1:] == '\n':
            return requestline[:-1]
        return requestline


    def handle_request(self):
        log.debug('HANDLING REQUEST')
        return self._handle_request_noblock(self)
        
        
    def _handle_request_noblock(self):
        log.debug('HANDLING NON_BLOCKING REQUEST')
        
        try:
            request, client_address = self.socket.accept()
        except Exception as e:
            log.error('Request buffer handle exception: %s' % e, exc_info=True)
            
        t = threading.Thread(target = self.process_request_thread,
                     args = (request, client_address))
        
        if self.daemon_threads:
            t.setDaemon (1)
            
        t.start()
        
        
    def process_request_thread(self, request, client_address):
        log.debug('Handling request with proxy from address %s' % client_address[0])
        
        try:
            rfile = request.makefile('rb')
            try:
                buffer = self.read_request(rfile)
            except CommandNotSupportedError as e:
                return self.send_error(request, 405)
                
            log.debug('Closing request...')
            rfile.close()
            
            log.debug('Creating client socket')
            
            try:
                client = socket.socket()
                client.connect(self.target_address)
            except Exception as e:
                return self.send_error(request, 503, e)
            
            log.debug('Writing request in client socket')
            wfile = client.makefile('wb')
            try:
                for line in buffer:
                    wfile.write(bytes(line, 'UTF-8'))
            except Exception as e:
                return self.send_error(request, 503, e)
            finally:
                log.debug('Closing client socket requests')
                wfile.close()
            
            wfile = request.makefile('wb')
            rfile = client.makefile('rwb')
            log.debug('Reading client response and writing to the main response')
            
            try:
                while True:
                    try:
                        line = next(rfile)
                        wfile.write(line)
                    except StopIteration:
                        break
                    
                return True
            
            except Exception as e:
                log.error(e, exc_info=True)
                
            finally:
                log.debug('Closing client response and request socket')
                rfile.close()
                wfile.close()
            
        except Exception as e:
            return self.send_error(request, 500, e)
        
        
    def send_error(self, request, code, message=None):
        if code not in ERRORS:
            error = 'Invalid error code %d' % code
            code = 500
        else:
            error = ERRORS[code]
            
        if not message is None:
            error = '%s %s' % (error, message)
            
        log.error(error, exc_info=True)
        
        error = 'HTTP/1.1 %d %s' % (code, error)
        
        wfile = request.makefile('wb')
        wfile.write(bytes(error, 'UTF-8'))
        wfile.close()
        return False
        
    def read_request(self, rfile):
        buffer = []
        command = None
        length = 0
        log.debug('Reading client request')
        while True:
            try:
                line = next(rfile).decode('UTF-8')
                buffer.append(line)
                
                if command is None:
                    command = str(line).split(' ')[0]
                    if command not in ['GET', 'POST']:
                        raise CommandNotSupportedError('Command %s is not supported' % command)
                        log.debug('command: {}'.format(command))
                
                if length == 0: 
                    if line.startswith('Content-Length:'):
                        length = int(line.split(' ')[1])
                        log.debug('content length: {}'.format(length))
                
                if not self.clean_line(line):
                    break
                
            except StopIteration:
                break
        
        log.debug('Reading Content up to {} chars'.format(length))
        while length > 0:
            if length > 1024:
                available = 1024
            else:
                available = length

            if available == 0:
                break
                
            line = rfile.read(available).decode('UTF-8')
            buffer.append(line)
            length -= len(line)

        log.debug('request from client read, size {}'.format(len(buffer)))
        return buffer
    

class CommandNotSupportedError(RuntimeError):
    pass


def __debug(message):
    
    sys.stdout.write(message)
    if not str(message).endswith('\n'):
        sys.stdout.write('\n')


if __name__ == '__main__':
    bs = BufferProxyServer('0.0.0.0', 7001, 7000)
    bs.start()
    while True:
        sys.stdout.write('Waiting connections...\n')
        time.sleep(50)
    
