#!/usr/bin/python
from __future__ import print_function
import redis
from rq import use_connection
import sys
from rq import Queue, Connection
from conn import run_img_rec, hello, ImgPack

def gen_queue(redis_server_url, redis_server_port, password):
    print('Establishing Redis connection...')
    print('  Server: %s' % redis_server_url)
    print('    Port: %s' % redis_server_port)
    q = Queue(connection=redis.Redis(host=redis_server_url, port=redis_server_port, password=password))
    return q

def run_job(img_path, queue):
    img_data = ImgPack(img_path, 'foo', 'bar')
    res = queue.enqueue(run_img_rec, img_data)
