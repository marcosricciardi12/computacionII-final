import socket
import argparse
import sys
import pickle
import time
import os

def download(sock):
    data = "download"
    data = pickle.dumps(data.encode())
    sock.sendall(bytes(data))

    msg = sock.recv(1024)
    aux_tam = sys.getsizeof(msg)
    while int(aux_tam)>=1024:
        aux = sock.recv(1024)
        aux_tam = sys.getsizeof(aux)
        msg = msg + aux

    if msg != b'':
        received = pickle.loads(msg).decode()
        print(received)

    storage_params = received.split('\n')
    HOST_ST, PORT_ST = str(storage_params[0]), int(storage_params[1])
    print("host: %s:%d" % (HOST_ST, PORT_ST))
    file = storage_params[4]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_st:
        sock_st.connect((HOST_ST, PORT_ST))
        data = 'download'
        data = pickle.dumps(data.encode())
        sock_st.sendall(bytes(data))

        data = str(file)
        data = pickle.dumps(data.encode())
        sock_st.sendall(bytes(data))

        msg = sock_st.recv(1024)
        aux_tam = sys.getsizeof(msg)
        while int(aux_tam)>=1024:
            aux = sock_st.recv(1024)
            aux_tam = sys.getsizeof(aux)
            msg = msg + aux

        if msg != b'':
            received = pickle.loads(msg).decode()
            print(received)       

def upload(sock):
    data = "upload"
    data = pickle.dumps(data.encode())
    sock.sendall(bytes(data))

    msg = sock.recv(1024)
    aux_tam = sys.getsizeof(msg)
    while int(aux_tam)>=1024:
        aux = sock.recv(1024)
        aux_tam = sys.getsizeof(aux)
        msg = msg + aux

    if msg != b'':
        received = pickle.loads(msg).decode()
        print(received)

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

            