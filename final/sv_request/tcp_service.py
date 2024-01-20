import socketserver
import signal, os
import subprocess as sp
import pickle
import sys
import socket
from compress_video_celery import compress_video
import time
from dotenv import load_dotenv
import os

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        print(self.client_address)
        self.st_addr_v4 = os.getenv('SV_ST_ADDR_V4_LOCAL').split(', ')
        self.st_addr_v4_ip , self.st_addr_v4_port = self.st_addr_v4[0], self.st_addr_v4[1]
        if self.st_addr_v4_ip[:8] == str(self.client_address[0][:8]):
            print("Soy local")
        self.st_addr_v6 = os.getenv('SV_ST_ADDR_V6').split(', ')
        self.st_addr_v6_ip , self.st_addr_v6_port = self.st_addr_v6[0], self.st_addr_v6[1]
        print(self.st_addr_v4_ip)
        self.data = self.request.recv(1024).strip()
        self.data = pickle.loads(self.data)
        self.data = self.data.decode()
        print(self.data)
        if self.data == 'upload':
            # self.task = compress_video.delay(self.data)
            # while not self.task.ready():
            #     time.sleep(1)
            #     print("Subiendo y comprimiendo video...")
            # self.output = self.task.get()
            # self.output = pickle.dumps(self.output.encode('ascii'))
            # self.request.sendall(self.output)
            # print(self.task.status)
            self.output = "%s\n%s\n%s\n%s\nruta/para/descargar/video" % (
                            self.st_addr_v4_ip , self.st_addr_v4_port,
                            self.st_addr_v6_ip , self.st_addr_v6_port)
            self.output = pickle.dumps(self.output.encode('ascii'))
            self.request.sendall(self.output) 
            #wait file upload confirmation
            # self.data = self.request.recv(1024).strip()
            # self.data = pickle.loads(self.data)
            # self.data = self.data.decode()
            # print(self.data)           
        
        if self.data == 'download':
            #
            self.output = "%s\n%s\n%s\n%s\nruta/para/descargar/video" % (
                            self.st_addr_v4_ip , self.st_addr_v4_port,
                            self.st_addr_v6_ip , self.st_addr_v6_port)
            self.output = pickle.dumps(self.output.encode('ascii'))
            self.request.sendall(self.output)
            print("ruta enviada al cliente")

        # while True:
        #     print("PID PADRE: %d" % os.getppid())
        #     print("PID: %d" % os.getpid())
        #     self.data = self.request.recv(1024).strip()
        #     print(sys.getsizeof(self.data))
        #     self.data = pickle.loads(self.data)
        #     self.process = sp.Popen(self.data, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        #     self.stdout, self.stderr = self.process.communicate()
        #     print("{} wrote:".format(self.client_address[0]))
        #     print(self.data)
        #     print(self.stdout)
        #     if self.stderr == b'':
        #         self.output = b'\nOK\n' + self.stdout
        #         self.output = pickle.dumps(self.output)
        #         self.request.sendall(self.output)
        #     else:
        #         self.output = b'\nERROR\n' + self.stderr
        #         self.output = pickle.dumps(self.output)
        #         self.request.sendall(self.output)
            

class ForkedTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class ForkedTCPServer6(socketserver.ForkingMixIn, socketserver.TCPServer):
    address_family = socket.AF_INET6

class ThreadedTCPServer6(socketserver.ThreadingMixIn, socketserver.TCPServer):
    address_family = socket.AF_INET6

def service4(host, port, concurrency):
    HOST, PORT = host, port
    socketserver.TCPServer.allow_reuse_address = True
    print()
    if concurrency == 'p':
        with ForkedTCPServer((HOST, PORT), MyTCPHandler) as server:
            print("IPV4: %s | Port: %s | Concurrency: %s MultiProcessing | Server PID: %d" % (host, port, concurrency, os.getpid()))
            server.serve_forever()
            server.shutdown()

    if concurrency == 't':
        with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
            print("IPV4: %s | Port: %s | Concurrency: %s Threading | Server PID: %d" % (host, port, concurrency, os.getpid()))
            server.serve_forever()
            try:
                signal.pause()
            except:
                server.shutdown()

def service6(host, port, concurrency):
    HOST, PORT = host, port
    socketserver.TCPServer.allow_reuse_address = True
    print()
    if concurrency == 'p':
        with ForkedTCPServer6((HOST, PORT), MyTCPHandler) as server:
            print("IPV6: %s | Port: %s | Concurrency: %s MultiProcessing | Server PID: %d" % (host, port, concurrency, os.getpid()))
            server.serve_forever()
            server.shutdown()

    if concurrency == 't':
        with ThreadedTCPServer6((HOST, PORT), MyTCPHandler) as server:
            print("IPV6: %s | Port: %s | Concurrency: %s Threading | Server PID: %d" % (host, port, concurrency, os.getpid()))
            server.serve_forever()
            try:
                signal.pause()
            except:
                server.shutdown()