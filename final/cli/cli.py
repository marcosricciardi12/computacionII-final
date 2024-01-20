import socket
import argparse
import sys
import pickle
import time
import os
import hashlib
import progressbar
import math

def send(data, sock):
    data = pickle.dumps(data.encode())
    sock.sendall(bytes(data))

def receive(sock):
    msg = sock.recv(1024)
    aux_tam = sys.getsizeof(msg)
    while int(aux_tam)>=1024:
        aux = sock.recv(1024)
        aux_tam = sys.getsizeof(aux)
        msg = msg + aux
    if msg != b'':
        received = pickle.loads(msg).decode()
        #print(received)
    return received

def download(sock):
    #send download action to sv_request
    send("download", sock)

    #wait sv_request response (response: sv_storage paramas connection)

    sv_storage_params = receive(sock).split('\n')
    HOST_ST, PORT_ST = str(sv_storage_params[0]), int(sv_storage_params[1])
    print("host: %s:%d" % (HOST_ST, PORT_ST))
    

    if not os.path.exists("download/"):
        os.makedirs("download/")

    #Client connect with sv_storage using received params from sv_request and send download action
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_st:
        
        sock_st.settimeout(3)
        #Client connect to sv_storage
        sock_st.connect((HOST_ST, PORT_ST))

        #Sv_storage wait 'download' option

        #Client send download to sv_storage
        send("download", sock_st)

        #Sv_storage Send list of available files

        #client wait and receive files_list   
        files_list = receive(sock_st).split('\n')

        #Client print list of files
        print("Video files:")
        for index, file in enumerate(files_list[:-1]):
            print("\t%d - %s" % (index+1, file))

        #Sv_storage wait the client sends the index to download
        #Client send index_file to sv_storage
        index = int(input("Enter the index of the file to download: "))-1
        send(str(index), sock_st)

        #Client wait and receive file_size to download
        file_size = receive(sock_st) 
        print("File size to download: %s" % file_size)
        file_size = int(file_size)
        factor = 1
        while file_size >= 1024:
            file_size = math.ceil(file_size/1024)
            factor = factor/1024
        #Sv_storage Send file

        #client receives file to download
        try:
            hash_file = hashlib.new('md5')
            with progressbar.ProgressBar(max_value=file_size, prefix="Downloading file: ") as bar:
                progress = 0
                progress_aux= 0
                with open("download/" + str(files_list[index]), 'wb') as file:
                    while True:
                        data = sock_st.recv(1024)
                        if not data:
                            break
                        # data = pickle.loads(data)
                        hash_file.update(data)
                        file.write(data)
                        if progress < file_size:
                            progress = int((progress_aux)*factor)+progress
                            progress_aux = progress_aux+1024
                        bar.update(progress)
        except socket.timeout:
            print("Tiempo de espera terminado")
            hash_file = str(hash_file.hexdigest())
            print("hash calculado: %s" % hash_file)

        #Sv_storage wait 'transmission ends'
            
        #Client send 'transmission ends' to sv_storage
        send("transmission_ends", sock_st)

        #Sv_storage Send original hash
        #client receives original hash
        original_hash = receive(sock_st) 
        print("Hash origen: %s" % original_hash)

        if original_hash == hash_file:
            print("File downloaded susccesfully!")
        else:
            print("Downloading file failed")




def upload(sock):

    send("upload", sock)

    #wait sv_request response (response: sv_storage paramas connection)
    sv_storage_params = receive(sock).split('\n')
    HOST_ST, PORT_ST = str(sv_storage_params[0]), int(sv_storage_params[1])
    #Client connect with sv_storage using received params from sv_request and send download action
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_st:
        sock_st.connect((HOST_ST, PORT_ST))
        #Sv_storage wait 'upload' option

        #Client send upload to sv_storage
        send("upload", sock_st)
        file_path = str(input("Enter the full path of the file to upload: "))
        file_name = file_path.split('/')
        file_name = str(file_name[-1])
        print("Name of file to upload: %s" % file_name)
        #Sv_storage wait 'file_size'

        #Client send file_size to sv_storage
        send(file_name, sock_st)

        hash_file = hashlib.new('md5')
        file_size = os.path.getsize(file_path)
        print(file_size)

        #Sv_storage wait 'file_size'

        #Client send file_size to sv_storage
        send(str(file_size), sock_st)
        factor = 1
        while file_size >= 1024:
            file_size = math.ceil(file_size/1024)
            factor = factor/1024
        
        with progressbar.ProgressBar(max_value=file_size, prefix="Uploading file: ") as bar:
            progress = 0
            progress_aux= 0
            with open(file_path, "rb") as file:
                data = file.read(1024)
                while data:
                    hash_file.update(data)
                    output = data
                    sock_st.sendall(output)
                    data = file.read(1024)
                    if progress < file_size:
                            progress = int((progress_aux)*factor)+progress
                            progress_aux = progress_aux+1024
                    bar.update(progress)
        hash_file = str(hash_file.hexdigest())
        print("hash md5: %s" % (hash_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="sdasdas")
    parser.add_argument("-j", "--host", type=str, required=True, help="Ingrese la direccion ip del host")
    parser.add_argument("-p", "--port", type=int, required=True, help="Ingrese el numero de puerto del host")
    parser.add_argument("-d", "--download", action='store_true',)
    parser.add_argument("-u", "--upload", action='store_true',)

    args = parser.parse_args()

    print(args.host, args.port)

    if args.download and args.upload:
        print("Elija solo una opcion: upload o download")
        os._exit(0)

    if not (args.download or args.upload):
        print("Elija al menos una opcion: upload o download")
        os._exit(0)

    HOST, PORT = args.host, args.port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        if args.download:
            download(sock)

        if args.upload:
            upload(sock)

            