import argparse
import socket
import time
import os
import json
from request import request

def is_socket_alive(sock):
    try:
        # Intenta obtener la opción de socket SO_KEEPALIVE
        sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
    except socket.error:
        # Si hay un error, la conexión probablemente está cerrada
        return False
    return True

def download():
    if not os.path.exists("download/"):
        os.makedirs("download/")
    print("List of files:")
    r = request(str(HOST), PORT, "get_files", {}, '')
    # print("Respuesta recibida del servidor:\nStatus: %s\nBody: %s\nFile: %s" % (r["status"], r["body"], r["file"]))
    body = json.loads(r["body"])
    files_list = body["Files list"]
    if not files_list:
        print("No files to download! try again later!")
        os._exit(0)
    quality_list = ["original", "medium", "low"]
    for index, file in enumerate(files_list):
        print("\t%d - %s" % (index+1, file))

    validate = True
    while validate:
        try:
            index_file = int(input("Enter the index of the file to download: "))-1
            if index_file < 0:
                raise ValueError
            files_list[index_file]
            validate = False
        except:
            print("No valid index, try again")

    for index, quality in enumerate(quality_list):
        print("\t%d - %s" % (index+1, quality))

    validate = True
    while validate:
        try:
            index_quality = int(input("Enter the index of the video Quality to download: "))-1
            if index_quality < 0:
                raise ValueError
            quality_list[index_quality]
            validate = False
        except:
            print("No valid index, try again")


    
    
    r = request(str(HOST), PORT, "get_file", {"name": files_list[index_file], "Quality" : quality_list[index_quality]}, '')
    print(r)
    r_body = json.loads(r["body"])
    os.rename(r_body["name"], "download/" + r_body["name"])

def upload():
    validate = True
    while validate:
        try:
            file_path = str(input("Enter the full path of the file to upload: "))
            if not os.path.isfile(file_path): raise NameError
            print(file_path[-3:])
            if file_path[-3:] != "mp4" and file_path[-3:] != "mkv": raise NameError
            validate = False
        except:
            print("Invalid path or not supported video file, try again!")
        

    file_name = file_path.split('/')
    file_name = str(file_name[-1])
    print("Name of file to upload: %s" % file_name)
    r = (request(str(HOST), PORT, "post_file", {"name" : file_name, "Quality": "original"}, file_path))
    print(r)
    r = (request(str(HOST), PORT, "compress_file", {"name" : file_name}, ''))
    print(r)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="sdasdas")
    parser.add_argument("-j", "--host", type=str, required=True, help="Ingrese la direccion ip del host")
    parser.add_argument("-p", "--port", type=int, required=True, help="Ingrese el numero de puerto del host")
    parser.add_argument("-d", "--download", action='store_true',)
    parser.add_argument("-u", "--upload", action='store_true',)
    args = parser.parse_args()

    print(args.host, args.port)

    HOST, PORT = args.host, args.port

    if args.download and args.upload:
        print("Elija solo una opcion: upload o download")
        os._exit(0)

    if not (args.download or args.upload):
        print("Elija al menos una opcion: upload o download")
        os._exit(0)

    if args.download:
        download()

    if args.upload:
        upload()

    # r = request(str(HOST), PORT, "get_file", {"name" : "123.mp4", "Quality" : "Original"}, '')
    # r = (request(str(HOST), PORT, "post_file", {"name" : "2023-12-06 17-52-36.mkv"}, '/home/marcos/2023-12-06 17-52-36.mkv'))
    # print(r)
