#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Corgan, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import os, sys, json, redis
from rq import Queue, Connection
import datetime

import rom
from rom import util
rom.util.use_null_session()

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

redis_host = REDIS_CONF['dbip']
redis_port = REDIS_CONF['port']
redis_pw   = REDIS_CONF['dbpasswd']
redis_num  = REDIS_CONF['dbnum']
util.set_connection_settings(host=redis_host, password=redis_pw, port=redis_port,  db=redis_num)

class Results(rom.Model) :
    results         = rom.OneToMany('ResultBase', column='transaction')
    transaction_id  = rom.Integer(required=True, unique=True, index=True)
    user_id         = rom.Integer(required=True, index=True)
    size_total_KB   = rom.Float(required=True)
    items_finished  = rom.Integer(required=True, default=0)
    items_total     = rom.Integer(required=True, default=0)


class ResultBase(rom.Model) :
    created_at     = rom.DateTime()
    finished_at    = rom.DateTime()
    item_number    = rom.Integer(required=True, index=True)
    item_name      = rom.String(index=True, required=True, keygen=rom.IDENTITY)
    status         = rom.String(index=True, required=True, keygen=rom.CASE_INSENSITIVE)
    size_KB        = rom.Float(required=True)
    transaction_id = rom.Integer(required=True, index=True)
    transaction    = rom.ManyToOne('Results', on_delete='set null')

    RESULT_ACTIVE   = "active"   # means the result is being computed
    RESULT_FINISHED = "finished" # means computation is finished
    RESULT_FAILED   = "failed"   # means computation failed
    RESULT_CANCELED = "canceled" # means the user canceled the transaction before this result was processed

