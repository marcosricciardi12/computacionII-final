from compress_video_celery_config import app
import time

@app.task
def compress_video(name):
    time.sleep(10)
    return "video %s was compressed." % (name)