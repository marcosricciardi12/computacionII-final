from compress_video_celery_config import app
import time

@app.task
def compress_video():
    time.sleep(10)
    return "video was compressed."