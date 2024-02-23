from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()
broker_addr = os.getenv('BROKER')
backend_addr = os.getenv('BACKEND')
ip_storage = os.getenv('IP_STORAGE')
port_storage = os.getenv('PORT_STORAGE')
app = Celery('compress_video_celery', broker=broker_addr, backend=backend_addr, include=['compress_video_celery'])