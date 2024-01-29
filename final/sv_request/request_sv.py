#!/usr/bin/python3
import time
import json
import subprocess
import os
from request import request
from dotenv import load_dotenv
from compress_video_celery import compress_video

load_dotenv()
st_addr_v4 = os.getenv('SV_ST_ADDR_V4').split(', ')
st_addr_v4_ip , st_addr_v4_port = st_addr_v4[0], int(st_addr_v4[1])
st_addr_v6 = os.getenv('SV_ST_ADDR_V6').split(', ')
st_addr_v6_ip , st_addr_v6_port = st_addr_v6[0], st_addr_v6[1]

def listen(c):
    index = 0
    index_struct = {
        0 : "action",
        1 : "body",
        2 : "file",
    }
    structure = {
        "action" : "",
        "body" : "",
        "file" : "",
    }
    sock = c
    size_block = 1024
    msg = sock.recv(size_block)
    header = False
    eot = False
        
    if bytes([1]) in msg:
        header = True
        # print("Inicio encabezado en posicion %d de %d" %(msg.index(bytes([1])), len(msg)))
        if bytes([1]) == bytes([msg[-1]]):
            msg = sock.recv(size_block)
        else:
            msg = msg[(msg.index(bytes([1])))+1:]
     
    while header and not eot and msg:
        for char in msg:
            if bytes([2]) == bytes([char]):
                pass
                # print("inicio texto")
            elif bytes([3]) == bytes([char]):
                # print("Fin texto")
                index = index + 1
            elif bytes([4]) == bytes([char]):
                # print("E O T")
                eot = True
                break
            else:
                # print("indice: %d" % index)
                structure[index_struct[index]] = structure[index_struct[index]] + str(bytes([char]).decode('ascii'))
        if not eot:
            msg = sock.recv(size_block)

    return (structure["action"],
            structure["body"],
            structure["file"],
            msg)

def exec_action(action, body_rcv , file_rcv, msg, sock):
    size_block = 1024
    end_file = bytes([0, 255]) * 512
    data_ant = b''

    body ={}

    if action == 'get_files':
        status = "Ok"
        file = ''
        r = request(st_addr_v4_ip, st_addr_v4_port, "get_files", {}, '')
        body.update(json.loads(r["body"]))
        body = json.dumps(body)
        return status, body, file
    

    #El cliente envia el archivo a guardar en el server de almacenamiento con la informacion del mismo en el body
    if action == 'post_file':
        file_path = body_rcv["name"]
        if (file_rcv):
            with open(file_path, 'wb') as file:
                if msg:
                    data_ant = msg[msg.index(bytes([4]))+1:]
                while True:
                    data = sock.recv(size_block)
                    super_data = data_ant + data
                    if not data:
                        break
                    if end_file in super_data:
                        # print(len(data))
                        print("endoffiletranssmision")
                        write_index = super_data.find(end_file)
                        file.write(data_ant[:write_index])
                        break
                    else:
                        file.write(data_ant)
                    data_ant = data
        
        
        comando = f"openssl dgst -{'md5'} '{file_path}'"
        
        # Ejecuta el comando y captura la salida
        resultado = subprocess.check_output(comando, shell=True)

        # Extrae el hash de la salida
        hash_calculado = resultado.split(b'= ')[1].strip().decode('utf-8')
        if hash_calculado == body_rcv["File to send hash"]:
            status = "Ok"
            # print("Source hash == Calculated hash")
            #Si el archivo recibido coincide con el enviado, se procede a enviar al servidor de almacenamiento
            r = request(st_addr_v4_ip , st_addr_v4_port, "post_file", body_rcv, file_path)
            print("Respuesta del servidor de almacenamiento: ")
            print(r)
            print()
            os.remove(file_path)
        else:
            status = "Error, received file is corrupt"
        body.update({'Received file hash' : hash_calculado})
        body = json.dumps(body)
        file = ''

        return status, body, file
    

    #En el body enviado por el cliente debe estar la clave "name" con el nombre del archivo solicitado
    if action == 'get_file':

        status = "Ok"
        file = ''
        #Solicita archivo al servidor donde se encuentre alojado, el nombre se encuentra en el body de la peticion del cliente
        #dentro de la funcion request, se establece comunicacion con el servidor de almacenamiento, el servidor responde con parametros y ademas el archivo requerido
        r = request(st_addr_v4_ip, st_addr_v4_port, "get_file", body_rcv, '')
        
        body.update(json.loads(r["body"]))
        print(body)
        file = body['name']
        os.rename(body_rcv["name"], body["name"])
        body = json.dumps(body)

        #se guarda el nombre del archivo solicitado por el cliente, asi al finalizar la respuesta, se envia finalmente el archivo deseado con informacion sobre el mismo en el body de respuesta
        

        return status, body, file
    
    if action == 'compress_file':
        file_path = body_rcv["name"]
        status = "Ok"
        file = ''
        task = compress_video.delay(file_path)
        while not task.ready():
            pass
        result = task.get()
        
        body.update({"Task result": result})
        print(body)

        body = json.dumps(body)

        return status, body, file


    
def response(status, body, file_path, sock):
    data = (bytes([1]) + 
            bytes([2]) + (status).encode('ascii') + bytes([3]) +
            bytes([2]) + (body).encode('ascii') + bytes([3]) +
            bytes([2]) + (file_path).encode('ascii') + bytes([3]) +
            bytes([4]))
    
    sock.sendall(bytes(data))

    if file_path:
        print(file_path)
        with open(file_path, "rb") as file:
            data = file.read(1024)
            while data:
                output = data
                sock.sendall(output)
                data = file.read(1024)

        end_file = bytes([0, 255]) * 512
        sock.sendall(bytes(end_file))
        os.remove(file_path)

def request_sv(c):
    print("Launching proc...")
    sock = c

    action, body_rcv , file_rcv, msg = listen(sock)
    body_rcv = json.loads(body_rcv)
    print("\nAccion recibida: %s \nBody recibido: %s\nArchivo a recibir: %s\n" % (action, body_rcv , file_rcv))

    status, body_snd, file_snd = exec_action(action, body_rcv , file_rcv, msg, sock)
    
    print("Respusta a Enviar: \nStatus: %s \nBody a enviar en la respuesta: %s\nArchivo a enviar: %s\n" % (status, body_snd , file_snd))

    response(status, body_snd, file_snd, sock)

    sock.close()
