Para instalar la aplicación primero se debe clonar el repositorio.
La apliación consta de diferentes partes: Un servidor de peticiones, un Servidor de almacenamiento y finalmente los workers.
Los servidores están implementados con entornos virtuales de python, de forma que como requisito previo es necesario que el sistema operativo donde se ejecutarán, deben disponer de dicha utilidad previamente instalada.

En las carpetas "sv_request", "sv_storage" y "worker", se encuentra disponible un script para desplegar el entorno virtual correspondiente a cada entorno de trabajo. Una vez dentro del directorió, bastará con ejecutar el archivo "install.sh"

Además, cada entorno de trabajo hace uso de variables de entorno para conectar los servicios entre si, de forma que es necesario editar dicho documento con las direcciones correspondiente a cada servicio que es necesario conectarse

Por último, es necesario tener una aplicación para el manejo de colas de tareas, como por ejemplo redis. Para esto en el equipo donde se ejecutará tal aplicación es necesario contar con Docker instalado previamente y correr una imagen de redis con el siguiente comando: "docker run -d -p 6379:6379 redis"
