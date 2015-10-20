#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the tasks that we can put into the various task queues.

from rq import Queue, Connection
import redis


class TaskQueue(object) :

    def __init__(self, redis_pool) :
        self.my_redis = redis.Redis(connection_pool=redis_pool)
        self.q = Queue(connection=self.my_redis)
        self.action_map = { "ocr" : process_pod_ocr, "bayes_spam" : process_pod_bayes_spam }

    def enqueue_pod(self, trans, fileh) :
        job = self.q.enqueue(process_pod_ocr, trans, fileh)
        return job
        

def process_pod_ocr(transaction, fileh) :
    print "trans details : " + str(transaction)
    print "file name     : " + fileh['name']
    print "file size     : " + str(fileh['size'])


def process_pod_bayes_spam(transaction, fileh) :
    print "trans : " + str(transaction) + "\n\n"
    print fileh['name']
    print fileh['size']
    
    
