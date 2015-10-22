#!/usr/bin/python
from __future__ import print_function
import redis
from rq import use_connection
import sys
from rq import Queue, Connection
from conn import run_img_rec, hello

def gen_queue(redis_server_url, redis_server_port, password):
    print('Establishing Redis connection...')
    print('  Server: %s' % redis_server_url)
    print('    Port: %s' % redis_server_port)
    q = Queue(connection=redis.Redis(host=redis_server_url, port=redis_server_port, password=password))
    return q

def run_job(img_path, queue):
    res = queue.enqueue(run_img_rec, img_path)

q = gen_queue('fileserver.local', 6379, '')
for i in range(1, len(sys.argv)):
    run_job(sys.argv[i], q)
