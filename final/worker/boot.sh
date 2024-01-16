source bin/activate
celery -A compress_video_celery worker --loglevel=INFO -c4
