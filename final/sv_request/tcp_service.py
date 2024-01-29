import socketserver
import signal, os
import subprocess as sp
import pickle
import sys
import hashlib
import socket
# from compress_video_celery import compress_video
import progressbar
import math
from request_sv import request_sv

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        request_sv(self.request)



            

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