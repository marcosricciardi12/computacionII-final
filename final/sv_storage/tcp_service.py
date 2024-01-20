import socketserver
import signal, os
import subprocess as sp
import pickle
import sys
import hashlib
import socket
from compress_video_celery import compress_video
import progressbar
import math

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def send(self, output):
        self.output = output
        self.output = pickle.dumps(self.output.encode('ascii'))
        self.request.sendall(self.output)

    def receive(self):
        self.data = self.request.recv(1024).strip()
        self.data = pickle.loads(self.data)
        self.data = self.data.decode()
        return self.data      

    def handle(self):
        #sv_storage accept connections
        #sv_storage receive a 'download' or 'upload' from client

        self.data = self.receive()
        print(self.data)

        #client could be direct user or workers processing video files
        #if receive a upload from client
        if self.data == 'upload':
            #sv_storage wait file name to upload
            self.file_name = self.receive()
            #sv_storage wait file size to upload
            self.file_size = math.ceil(float(self.receive()))
            self.factor = 1
            while self.file_size >= 1024:
                self.file_size = math.ceil(self.file_size/1024)
                self.factor = self.factor/1024
            print("File name: %s | File size: %s" % (self.file_name, self.file_size))
            hash_file = hashlib.new('md5')
            with progressbar.ProgressBar(max_value=self.file_size, prefix="Receiving file: ") as bar:
                progress = 0
                progress_aux= 0
                with open("files/original/" + str(self.file_name), 'wb') as file:
                    while True:
                        data = self.request.recv(1024)
                        if progress < self.file_size:
                            progress = int((progress_aux)*self.factor)+progress
                            progress_aux = progress_aux+1024
                        bar.update(progress)
                        if not data:
                            break
                        # data = pickle.loads(data)
                        hash_file.update(data)
                        file.write(data)
            hash_file = str(hash_file.hexdigest())
            print("hash calculado: %s" % hash_file)


        #if receive a download from client
        if self.data == 'download':
            print("Hay que enviar una lista de archivos disponibles para descargar")
            p = sp.Popen("ls files/original/", stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            stdout, stderr = p.communicate()
            stdout = stdout.decode() #
            files_list = stdout.split('\n')

            #sv_storage send files list            
            self.send(stdout)
            #files_list sent

            #receive from client index file to send
            self.data = self.receive()
            print(self.data)
            self.index = int(self.data)
            #index received from client

            #sv_storage send file size to download
            file_size = os.path.getsize(f"files/original/" + str(files_list[self.index]))
            factor = 1
            self.send(str(file_size))

            while file_size >= 1024:
                file_size = math.ceil(file_size/1024)
                factor = factor/1024
            #sv_storage send file to download and generate hash file
            self.hash_file = hashlib.new('md5')
            with progressbar.ProgressBar(max_value=file_size, prefix="Sending file: ") as bar:
                progress = 0
                progress_aux= 0
                with open("files/original/" + str(files_list[self.index]), "rb") as file:
                    self.data = file.read(1024)
                    while self.data:
                        self.hash_file.update(self.data)
                        self.output = self.data
                        self.request.sendall(self.output)
                        self.data = file.read(1024)
                        if progress < file_size:
                            progress = int((progress_aux)*factor)+progress
                            progress_aux = progress_aux+1024
                        bar.update(progress)
            self.hash_file = str(self.hash_file.hexdigest())
            print("hash md5: %s" % (self.hash_file))

            #sv_storage wait and receive a 'transmission ends' or 'upload' from client

            self.data = self.receive()
            print(self.data)

            #sv_storage send hash_file         
            self.hash_file
            print("output md5: %s" % (self.hash_file))
            self.send(self.hash_file)
            #hash_file sent



            

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