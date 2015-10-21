#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the tasks that we can put into the various task queues.

import os, sys, json, redis
from rq import Queue, Connection

from flask import jsonify
import sqlalchemy

import datetime


# @info - takes a given json file and loads it into an active dictionary for return
def load_json_file(fn) :
    if os.path.isfile(fn) :                                                                                                                          
        with open(fn, 'r+') as fh :
            data = json.load(fh)
        return data
    return None

DB_CONF_FILE  = os.path.expanduser("~") + "/.praxyk/dbconfig/config"
dbconf        = load_json_file(DB_CONF_FILE)
REDIS_CONF    = dbconf['redisdb']

class TaskQueue(object) :

    def __init__(self, redis_pool) :
        self.my_redis = redis.Redis(connection_pool=redis_pool)
        self.q = Queue(connection=self.my_redis)
        self.action_map = { "ocr" : process_pod_ocr, "bayes_spam" : process_pod_bayes_spam }

    def enqueue_pod(self, trans, fileh) :
        job = self.q.enqueue(process_pod_ocr, trans, fileh)
        return job
        
def get_redis_conn() :
    redis_host = REDIS_CONF['dbip']
    redis_port = REDIS_CONF['port']
    redis_pw   = REDIS_CONF['dbpasswd']
    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, password=redis_pw)
    return redis_pool


def get_sql_conf() :
    dbuser     = dbconf['dbuser']                                                                                                                        
    dbip       = dbconf['dbip']
    dbpasswd   = dbconf['dbpw']
    dbname     = dbconf['dbname']
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (dbuser, dbpasswd, dbip, dbname) 
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    connection = engine.connect()

def convert_timestr(dt) :
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def process_pod_ocr(transaction, fileh) :
    results_key = "results:%s" %str(transaction['trans_id'])
    results_user_id = results_key+":user_id"
    results_items_list = results_key+":items"
    results_count = results_key+":count"
    results_finished = results_key+":finished"

    print "POD-OCR Worker Starting"
    print "result id     : " + results_key+":item:%s"%str(transaction['file_num'])
    print "file name     : " + fileh['name']
    print "file size     : " + str(fileh['size'])

    
    result_item_args = {
                         "item_id" : transaction['file_num'],
                         "return_string" : "I did not read this with OCR technology",
                         "finished_at"   : convert_timestr(datetime.datetime.now())
                        }

    result_item_json = json.dumps(result_item_args)
    
    rdb_pool = get_redis_conn()
    rdb = redis.Redis(connection_pool=rdb_pool)
    rdb.lpush(results_items_list, result_item_json)
    rdb.incr(results_count)

    print "POD_OCR Worker Finished"

    if int(rdb.get(results_count)) == int(transaction['files_total']) :
        rdb.set(results_finished, 1)

    # rdb_pool.release(rdb.connection())

    return result_item_json


def process_pod_bayes_spam(transaction, fileh) :
    print "trans : " + str(transaction) + "\n\n"
    print fileh['name']
    print fileh['size']
    
    
