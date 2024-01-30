from celery import Celery
import multiprocessing

app = Celery('myapp', broker='redis://127.0.0.1:6379')

@app.task
def tarea_principal():
    # Tarea principal
    print("Inicio de la tarea principal")

    # Ejecutar subprocesos
    procesos = []
    for i in range(3):
        proceso = multiprocessing.Process(target=subproceso, args=(i,))
        procesos.append(proceso)
        proceso.start()

    # Esperar a que todos los subprocesos terminen
    for proceso in procesos:
        proceso.join()

    print("Fin de la tarea principal")

def subproceso(numero):
    # Código del subproceso
    print(f"Subproceso {numero} iniciado")

    # Realizar operaciones en el subproceso

    print(f"Subproceso {numero} finalizado")

if __name__ == '__main__':
    tarea_principal.delay()
