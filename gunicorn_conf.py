# gunicorn_conf.py
from multiprocessing import cpu_count

bind = "0.0.0.0:7000"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

