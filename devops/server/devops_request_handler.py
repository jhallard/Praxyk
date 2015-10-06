#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

########################################################################################
#                                DEVOPS REQUEST HANDLER                                #
#                    " Server-side shared-resource API manager  "                      #
#  This is the main request handler for the shared-compute-resource management         #
#  system. It exposes an API to create, image, and destroy virtual machines            #
#  of various sizes from mutiple different service providers. All API calls            #
#  must be validated with 512bit tokens that the user stores locally.                  #
#                                                                                      #
#                                     Arguments                                        #
#  Use -h or --help to print script help                                               #
#
#
########################################################################################

from vm_util import *
from auth_util import *
from devops_util import *
from log_util import *
from db_util import *

import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify


## logging directories
BASEDIR = "../logs/"
LOG_DIR_VM = BASEDIR + "vm-logs/"
LOG_DIR_DB = BASEDIR + "db-logs/"
LOG_DIR_SERVER = BASEDIR + 'server-logs'
LOG_DIR_COMB = BASEDIR + "comb-logs/"
LOG_DIR_AUTH = BASEDIR + "auth-logs/"
LOG_DIR_DEVOPS = BASEDIR + "devops-logs/"
LOGDIR_HANDLER = BASEDIR + "handler-logs/"
LOG_DIR_TEST = BASEDIR + "test-logs/"


## logutil client names
VM_LOG_CLIENT = 'vmclient'
DB_LOG_CLIENT = 'dbclient'
AUTH_LOG_CLIENT = 'authclient'
SERVER_LOG_CLIENT = 'serverclnt'
DEVOPS_LOG_CLIENT = 'devopsclnt'
HANDLER_LOG_CLIENT = 'handlerclnt'

DEVOPS_HANDLER_APP = Flask(__name__)

DESCRIPTION = """
This is the set of unit tests for that devops server backend.
From this program you can test the main server program as well
as the various utilities that it relies on, like the dbUtil,
vmUtil, and authUtil classes.
"""

# @info - parse command line args into useable dictionary
#         right now we only take a config file as an argument
def parse_args(argv) :
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--metaconfig', help="Full path to the json file containing info " + \
                                             "about the meta-database for storing log files.")
    parser.add_argument('--schemaf', help="Full path to the .schema file for a database. This is required if " + \
                                          "you are testing the datbase, auth, devops, or server.")
    parser.add_argument('--flags', help="A string where each character represents a test flag. Only used for vmtest so far." + \
                                        "vmtest flags : [a b c d e f] each one runs another series of tests.")
    parser.add_argument('config', help="Full path to the config file for this regression. It should include " + \
                                       "the vm tokens, dbip, dbpw, and dbuser.")
    parser.add_argument('test', help="Which test do you want to run. The following are accepted : " + \
                                     "{vmtest, authtest, devopstest, servertest, dbtest}")
    return parser.parse_args()

# @info - loads the given json file path into a dictionary and returns it
def parse_config_file(fn) :
    if os.path.isfile(fn) :
        with open(fn, 'r+') as fh :
            data = json.load(fh)
        return data
    return None


# @info - formats the log filenames in a consistent format, client+datetime+.log in the clients own directory.
def formatfn(logdir, client, dt) :
    dt = dt.replace(" ", "_")
    return logdir+client+'_'+dt +'.log'

# @info - logUtil is class that serves as a global log multiplexer. It takes a bunch of clients and maps
#         all of their logging inputs to any series of defined logging outputs. Log outputs can be both
#         filenames and std streams. Since this is the top level of the program, we init the logUtil here,
#         and tell everyone where they're going to log. We then pass around the logutil object and the 
#         logging works out uniformly. See @/lib/log_util.py for more info.
def init_logutil() :
    logutil = logUtil()
    dt = logutil.date_timestamp_str()
    clients = {
             # client-name  --maps to---> [    list of filename or streams        ]
               VM_LOG_CLIENT            : [formatfn(LOG_DIR_VM, VM_LOG_CLIENT, dt)],
               DB_LOG_CLIENT            : [formatfn(LOG_DIR_DB, DB_LOG_CLIENT, dt)],
               AUTH_LOG_CLIENT          : [formatfn(LOG_DIR_AUTH, AUTH_LOG_CLIENT, dt)],
               SERVER_LOG_CLIENT        : [formatfn(LOG_DIR_SERVER, SERVER_LOG_CLIENT, dt)],
               DEVOPS_LOG_CLIENT        : [formatfn(LOG_DIR_DEVOPS, DEVOPS_LOG_CLIENT, dt)],
               HANDLER_LOG_CLIENT       : [sys.stdout, formatfn(LOG_DIR_HANDLER, HANDLER_LOG_CLIENT, dt)]
               logutil.error_client_name: [sys.stderr], # uncmnt to direct all errors to stderr
               logutil.combined_client_name : [formatfn(LOG_DIR_COMB, logutil.combined_client_name, dt)]}
    logutil.set_clients(clients)
    return (logutil, dt) 



tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

if __name__ == '__main__':
    args = parse_args(sys.argv)
    arg_map = parse_config_file(args.config) 
    (logutil, db) = init_logutil()

    if not arg_map:
        sys.stderr.write("Failed to parse input configuration file.")
        sys.exit(1)

    DEVOPS_HANDLER_APP.run(debug=True)


