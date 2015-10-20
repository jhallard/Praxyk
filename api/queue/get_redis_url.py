#!/usr/bin/python

import os
import sys
import json
import subprocess

DBFILE = os.path.expanduser("~")+"/.praxyk/dbconfig/config"

# @info - takes a given json file and loads it into an active dictionary for return
def load_json_file(fn) :
    if os.path.isfile(fn) :    
        with open(fn, 'r+') as fh :
            data = json.load(fh)
        return data
    return None

def gen_redis_url() :
    dbconf = load_json_file(DBFILE)
    redisdb = dbconf['redisdb']
    dbip = dbconf['dbip']
    pw = redisdb['dbpasswd']
    port = redisdb['port']
    return (pw, dbip, port)

if __name__ == '__main__' : 
    server = gen_redis_url()
    server = "redis://:%s@%s:%s" % (server[0], server[1], server[2])
    print server


    

