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


DB_CONF_FILE = os.path.expanduser("~") + "/.praxyk/dbconfig/config"
dbconf = load_json_file(DB_CONF_FILE)
dbuser = dbconf['dbuser']
dbip = dbconf['dbip']
dbpasswd = dbconf['dbpw']
dbname = dbconf['dbname']

SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (dbuser, dbpasswd, dbip, dbname)
SQLALCHEMY_ECHO = False                                                                               

SECRET_KEY = os.urandom(24)

DEBUG = False       
