from redislite import Redis
from rq import Worker, Queue, Connection
from config import REDIS_DB

listen = ['default']


with Connection(connection=Redis(REDIS_DB)):
    worker = Worker(list(map(Queue, listen)))
    worker.work()