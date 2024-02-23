Para correr "sv_request": ejecutar boot.sh en el directorio sv_request/
    Corre el servidor de peticiones en el puerto 8080 en modo multiproceso
    Modificar .env con las URL correspondientes para conectarse a la cola de tareas de redis, y la URL correspondiente al servidor de Almacenamiento.

Para correr "sv_storage": ejecutar boot.sh en el directorio sv_storage/
    Corre el servidor de peticiones en el puerto 5005 en modo multiproceso
    Modificar .env con las URL correspondientes para conectarse.

Para correr "worker": ejecutar boot.sh en el directorio worker/
    Ejecuta el worker que trabaja haciendo uso de Celery, conectando a la cola de tareas y al backend.
    Modificar .env con las URL correspondientes para conectarse a la cola de tareas de redis, y la URL correspondiente al servidor de Almacenamiento.

Cliente:
    Descargar videos:

    ejecutar dentro de cli/ : "python3 cli.py -j "ip_server_request" -p "port_server_request" -d

        Luego se mostrará una lista de los archivos disponibles, y el usuario deberá ingresar por teclado el número correspondiente al indice del archivo a descargar
        Finalmente elegirá por teclado la calidad deseada del archivo a descargar, introduciendo nuevamente el indice correspondiente a las calidades mostradas en pantalla.

    Subir videos:

    ejecutar dentro de cli/ : "python3 cli.py -j "ip_server_request" -p "port_server_request" -u

    Ingresar el path completo del video que se desea subir, y eso será todo.
