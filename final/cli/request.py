import time, socket, json, os, subprocess

def request(host, port, action, body, file):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))

        if file:
            comando = f"openssl dgst -{'md5'} '{str(file)}'"
            resultado = subprocess.check_output(comando, shell=True)

            # Extrae el hash de la salida
            hash_calculado = resultado.split(b'= ')[1].strip().decode('utf-8')
            body.update({'File to send hash' : hash_calculado})

        body = json.dumps(body)
        data = (bytes([1]) + 
                bytes([2]) + (action).encode('ascii') + bytes([3]) +
                bytes([2]) + (body).encode('ascii') + bytes([3]) +
                bytes([2]) + (file).encode('ascii') + bytes([3]) +
                bytes([4]))
        
        sock.sendall(bytes(data))

        if file:
            with open(file, "rb") as file:
                data = file.read(1024)
                while data:
                    output = data
                    sock.sendall(output)
                    data = file.read(1024)

            end_file = bytes([0, 255]) * 512
            sock.sendall(bytes(end_file))
        time.sleep(1)


        index = 0
        index_struct = {
            0 : "status",
            1 : "body",
            2 : "file",
        }
        structure = {
            "status" : "",
            "body" : "",
            "file" : "",
        }
        size_block = 1024
        msg = sock.recv(size_block)
        header = False
        eot = False
        end_file = bytes([0, 255]) * 512
        data_ant = b''       
            
        if bytes([1]) in msg:
            header = True
            # print("Inicio encabezado en posicion %d de %d" %(msg.index(bytes([1])), len(msg)))
            if bytes([1]) == bytes([msg[-1]]):
                msg = sock.recv(size_block)
            else:
                msg = msg[(msg.index(bytes([1])))+1:]
        
        data = b''
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
        
        if (structure["file"]):
            with open(structure["file"], 'wb') as file:
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

    return(structure)