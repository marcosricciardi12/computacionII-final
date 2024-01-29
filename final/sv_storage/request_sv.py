#!/usr/bin/python3
import time
import json
import subprocess

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
        print("Hay que enviar una lista de archivos disponibles para descargar")
        p = subprocess.Popen("ls files/original/", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        stdout = stdout.decode() #
        files_list = stdout.split('\n')
        body.update({"Files list" : files_list[:-1]})
        body = json.dumps(body)    
        return status, body, file
    
    if action == 'post_file':
        if (file_rcv):
            with open("files/original/" + file_rcv, 'wb') as file:
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
        
        
        comando = f"openssl dgst -{'md5'} 'files/original/{file_rcv}'"
        
        # Ejecuta el comando y captura la salida
        resultado = subprocess.check_output(comando, shell=True)

        # Extrae el hash de la salida
        hash_calculado = resultado.split(b'= ')[1].strip().decode('utf-8')
        if hash_calculado == body_rcv["File to send hash"]:
            status = "Ok"
            # print("Source hash == Calculated hash")
        else:
            status = "Error, received file is corrupt"
        body.update({'Received file hash' : hash_calculado})
        body = json.dumps(body)
        file = ''

        return status, body, file
    
    if action == 'get_file':
        quality = {"Original" : "files/original/",
                   "Medium": "files/medium/",
                   "Low": "files/low/"}
        file_path = quality[body_rcv["Quality"]] + body_rcv['name']
        status = "Ok"
        comando = f"openssl dgst -{'md5'} '{file_path}'"
        
        # Ejecuta el comando y captura la salida
        resultado = subprocess.check_output(comando, shell=True)

        # Extrae el hash de la salida
        hash_calculado = resultado.split(b'= ')[1].strip().decode('utf-8')
        body.update({"name": body_rcv["Quality"] + " - " + body_rcv['name'], 'Source hash' : hash_calculado, "File": file_path})
        body = json.dumps(body)
        file = body_rcv['name']

        return status, body, file
    
def response(status, body, file, sock):
    data = (bytes([1]) + 
            bytes([2]) + (status).encode('ascii') + bytes([3]) +
            bytes([2]) + (body).encode('ascii') + bytes([3]) +
            bytes([2]) + (file).encode('ascii') + bytes([3]) +
            bytes([4]))
    
    sock.sendall(bytes(data))

    if file:
        body = json.loads(body)
        file_path = body["File"]
        with open(file_path, "rb") as file:
            data = file.read(1024)
            while data:
                output = data
                sock.sendall(output)
                data = file.read(1024)

        end_file = bytes([0, 255]) * 512
        sock.sendall(bytes(end_file))
        time.sleep(1)

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
