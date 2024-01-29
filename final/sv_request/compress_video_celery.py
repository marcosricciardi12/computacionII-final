from compress_video_celery_config import app
import time
from request import request
import os
from multiprocessing import Process
from moviepy.editor import VideoFileClip


@app.task
def compress_video(name):
    if not os.path.exists("files_to_send/"):
        os.makedirs("files_to_send/")
    if not os.path.exists("files_to_send/medium/"):
        os.makedirs("files_to_send/medium/")
    if not os.path.exists("files_to_send/low/"):
        os.makedirs("files_to_send/low/")

    host = "192.168.54.199"
    port = 5005
    quality_list = ["medium", "low"]
    procesos = []
    r = request(str(host), port, "get_file", {"name": name, "Quality" : "original"}, '')
    time.sleep(1)
    for quality in quality_list:
        compress(name, quality, host, port)
    os.remove(name)
    return "video %s was compressed." % (name)

def compress(name, quality, host, port):
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
        
    except Exception as e:
        print(f"Error al comprimir el video: {e}")