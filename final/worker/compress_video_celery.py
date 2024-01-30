from compress_video_celery_config import app
import time
from request import request
import os
from billiard import Process
from moviepy.editor import VideoFileClip
import subprocess

@app.task
def compress_video(name):
    if not os.path.exists("files_to_send/"):
        os.makedirs("files_to_send/")
    if not os.path.exists("files_to_send/medium/"):
        os.makedirs("files_to_send/medium/")
    if not os.path.exists("files_to_send/low/"):
        os.makedirs("files_to_send/low/")
    #Storage address
    host = "192.168.54.199"
    port = 5005
    quality_list = ["medium", "low"]
    procesos = []
    r = request(str(host), port, "get_file", {"name": name, "Quality" : "original"}, '')
    time.sleep(1)
    for quality in quality_list:
        # compress(name, quality, host, port)
        proceso = Process(target=compress, args=(name, quality, host, port, ), force=True)
        procesos.append(proceso)
        proceso.start()
    for proceso in procesos:
        proceso.join()
    os.remove(name)
    return "video %s was compressed." % (name)

def compress(name, quality, host, port):
    # Obtener la resolución original del video
    cmd_resolucion = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', name]
    resolucion_original = subprocess.check_output(cmd_resolucion, universal_newlines=True).strip().split('x')
    quality_factor = {"medium": 0.5, "low": 0.25}
    output_path = "files_to_send/" + quality + "/" + name
    # Calcular la nueva resolución
    nueva_resolucion = f"{int(float(resolucion_original[0]) * quality_factor[quality])}x{int(float(resolucion_original[1]) * quality_factor[quality])}"

    # Obtener el bitrate original del video
    cmd_bitrate = ['ffprobe', '-v', 'error', '-show_entries', 'format=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', name]
    bitrate_original = int(subprocess.check_output(cmd_bitrate, universal_newlines=True).strip())

    # Calcular el nuevo bitrate
    nuevo_bitrate = int((float(bitrate_original) * quality_factor[quality])/1024)

    # Ejecutar el comando ffmpeg
    cmd_ffmpeg = [
        'ffmpeg',
        '-i', name,
        '-vf', f'scale={nueva_resolucion}',
        '-b:v', f'{nuevo_bitrate}k',
        '-c:a', 'copy',
        output_path
    ]

    subprocess.run(cmd_ffmpeg, check=True)
    print(f"Video comprimido con éxito: {output_path}")
    r = (request(str(host), port, "post_file", {"name" : name, "Quality": quality}, output_path))
    os.remove(output_path)


def compress_old(name, quality, host, port):
    try:
        # Cargar el video
        quality_factor = {"medium": 0.5, "low": 0.25}
        video = VideoFileClip(name)
        output_path = "files_to_send/" + quality + "/" + name 
        # Comprimir el video con un bitrate específico
        compressed_clip = video.resize(width=video.size[0] * quality_factor[quality], height=video.size[1] * quality_factor[quality])
        compressed_clip.write_videofile(output_path, bitrate="500k")
        print(f"Video comprimido y guardado en {output_path}.")
        r = (request(str(host), port, "post_file", {"name" : name, "Quality": quality}, output_path))
        os.remove(output_path)
    except Exception as e:
        print(f"Error al comprimir el video: {e}")        