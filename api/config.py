#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines the configuration settings for the Flask handler,
##         sqalchemy DB connections, and more.
import os                                                                                             
import os.path
import json

# @info - takes a given json file and loads it into an active dictionary for return
def load_json_file(fn) :
    if os.path.isfile(fn) :            
        with open(fn, 'r+') as fh :
            data = json.load(fh)
        return data
    return None


DB_CONF_FILE  = os.path.expanduser("~") + "/.praxyk/dbconfig/config"
API_CONF_FILE = os.path.expanduser("~") + "/.praxyk/apiconfig/rootconfig"
dbconf        = load_json_file(DB_CONF_FILE)
apiconf       = load_json_file(API_CONF_FILE)

dbuser     = dbconf.get('dbuser', "")
dbip       = dbconf.get('dbip', "")
dbpasswd   = dbconf.get('dbpw', "")
dbname     = dbconf.get('dbname', "")
REDIS_CONF = dbconf.get('redisdb', "")

RQ_DEFAULT_HOST = REDIS_CONF.get('dbip', "")
RQ_DEFAULT_PORT = REDIS_CONF.get('port', "")
RQ_DEFAULT_PASSWORD = REDIS_CONF.get('dbpasswd', "")
# RQ_DEFAULT_DB = 1

SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (dbuser, dbpasswd, dbip, dbname)
SQLALCHEMY_ECHO         = True

SECRET_KEY = os.urandom(24)

DEBUG = True
