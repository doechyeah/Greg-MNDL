import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']
conn = redis.from_url('redis://localhost:6379/0')

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()