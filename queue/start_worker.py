#!/usr/bin/env python

# Preload libraries
# import __init__
import task_lib

import sys, json, os, redis
from rq import Queue, Connection, Worker


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

if __name__ == '__main__' :
    # try :
        redis_host = REDIS_CONF['dbip']
        redis_port = REDIS_CONF['port']
        redis_pw   = REDIS_CONF['dbpasswd']
	print REDIS_CONF
	my_redis = redis.Redis(host=redis_host, port=redis_port, password=redis_pw, db=1)
        q = Queue(connection=my_redis)

        w = Worker(q)
        w.work()
    # except Exception, e :
        # print "Error exception" + str(e)
