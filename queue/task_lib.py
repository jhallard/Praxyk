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

from models.nosql.pod.result_pod_ocr import *
from api import *

import datetime

import praxyk


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
    redis_num  = REDIS_CONF['dbnum']
    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, password=redis_pw, db=redis_num)
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

STORE_BASENAME = os.path.dirname(os.path.realpath(__file__)) + "/images/"
def process_pod_ocr(transaction, fileh) :
    print "POD-OCR Worker Starting"
    print "result id     : " + str(transaction['file_num'])
    print "file name     : " + fileh['name']
    print "file size     : " + str(fileh['size'])

    trans_id = transaction['trans_id']
    file_num = transaction['file_num']
    files_total = transaction['files_total']

    app_context = PRAXYK_API_APP.app_context()
    app_context.push()

    trans = Transaction.query.get(trans_id) # gets the sql transaction object from the db

    # this if statement checks if the trans has been canceled, if so we mark this result as canceled
    # and return right away, avoiding further computation
    if trans.status == Transaction.TRANSACTION_CANCELED :
        this_result = Result_POD_OCR.query.filter(transaction_id=trans_id).filter(item_number=file_num).first()
        if this_result :
            this_result.finished_at = datetime.datetime.now()
            this_result.status = Result_POD_OCR.RESULT_CANCELED
            this_result.result_string = ""
            this_result.save()
            app_context.pop()
        return this_result

    imgs_dir = STORE_BASENAME + str(trans_id)
    if not os.path.exists(imgs_dir):
        os.makedirs(imgs_dir)

    file_img = imgs_dir+fileh['name']+'_'+str(file_num)
    print file_img
    with open(file_img, 'wr+') as fh :
        fh.write(fileh['data'])

    # get the individual result struct from redis that this queue task is processing
    this_result = Result_POD_OCR.query.filter(transaction_id=trans_id).filter(item_number=file_num).first()

    if not this_result :
        print "POD_OCR Worker Error, Can't Find This Result"
        return False

    # update this result object in the redis db
    this_result.finished_at = datetime.datetime.now()
    this_result.status = Result_POD_OCR.RESULT_FINISHED
    this_result.result_string = praxyk.get_string_from_image(file_img)
    this_result.save()

    # clean up the image space used
    os.remove(file_img)

    results = Results.query.filter(transaction_id=trans_id).first() # gets the redis transaction
                                                                    # object that contains indiv.
                                                                    # result information
    if not results :
        print "POD_OCR Worker Error, Can't Find Results"
        return False

    # update the transaction object (group of results) in the redis db
    # super hacky way to avoid data races on items_finished
    results.items_finished += 1
    results.save()

    if results.items_finished  == results.items_total :
        # @TODO - remove the directory for this set of results
        trans.finished_at = datetime.datetime.now()
        trans.status = Transaction.TRANSACTION_FINISHED
        db.session.commit()

    print "POD_OCR Result String : (%s) " % this_result.result_string
    print "POD_OCR Worker Finished"
    app_context.pop()

    return this_result


def process_pod_bayes_spam(transaction, fileh) :
    print "trans : " + str(transaction) + "\n\n"
    print fileh['name']
    print fileh['size']
    
    
