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
import _fix_path_
from vm_util import *
from auth_util import *
from devops_util import *
from log_util import *
from db_util import *

import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify, request, Response, g
from functools import wraps


## logging directories
BASEDIR = "logs/"
LOG_DIR_VM = BASEDIR + "vm-logs/"
LOG_DIR_DB = BASEDIR + "db-logs/"
LOG_DIR_SERVER = BASEDIR + 'server-logs'
LOG_DIR_COMB = BASEDIR + "comb-logs/"
LOG_DIR_AUTH = BASEDIR + "auth-logs/"
LOG_DIR_DEVOPS = BASEDIR + "devops-logs/"
LOG_DIR_HANDLER = BASEDIR + "handler-logs/"


## logutil client names
VM_LOG_CLIENT = 'vmclient'
DB_LOG_CLIENT = 'dbclient'
AUTH_LOG_CLIENT = 'authclient'
SERVER_LOG_CLIENT = 'serverclnt'
DEVOPS_LOG_CLIENT = 'devopsclnt'
HANDLER_LOG_CLIENT = 'handlerclnt'

IMAGE_DEFAULT = 13089493 # ubuntu 140-04 x64
CLASS_SLUG_DEFAULT = '2gb'

PROVIDER_DEFAULT = "DO"
REGION_DEFAULT = "sfo1"

global CONFIG
global SCHEMA

DEVOPS_HANDLER_APP = Flask(__name__)

DESCRIPTION = """
This is the script that handles all incoming API requests for the
Praxyk development operations server (devops.praxyk.com). It uses the
included utilities (vmUtil, dbUtil, authUtil, devopsUtil) to expose a
secure and simple interface for users to access shared compute resources.

The script must be given the path to a configuration file containing sensitive
information (dbusers, dbpw, dbip, auth tokens for IaaS providers). It also must
be given a shema file representing the devops database that is being used.

Most actions that are performed by this script are triggered via incoming API calls,
except for the build/fill database commands. Those can only be triggered by giving the
input flag --builddb and --filldb respectively. Build DB will cause the tables and indexes
to be constructed, while fill DB will cause data in the DB to be synced with data from
IaaS providers. It will also add in the root user. 

If you want to sync the DB with IaaS providers manually without building and filling the DB
from scratch, you can use the API to send a sync command. See the DevOps API Docs.
"""

# @info - parse command line args into useable dictionary
#         right now we only take a config file as an argument
def parse_args(argv) :
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--metaconfig', help="Full path to the json file containing info " + \
                                             "about the meta-database for storing log files.")
    parser.add_argument('--builddb', help="If present, the DB represented by the given schema file will be"+\
                                    "built from scratch but not filled, given that it doesn't exist already.")
    parser.add_argument('--filldb', help="If present, the devops DB that was just built will be synced with"+\
                                    "the current info provided by IaaS providers.")
    parser.add_argument('config', help="Full path to the config file for this regression. It should include " + \
                                       "the vm tokens, dbip, dbpw, and dbuser.")
    parser.add_argument('schemaf', help="Full path to the .schema file for a database.")
    return parser.parse_args()


# @info - takes a given json file and loads it into an active dictionary for return
def load_json_file(fn) :
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
               HANDLER_LOG_CLIENT       : [formatfn(LOG_DIR_HANDLER, HANDLER_LOG_CLIENT, dt)],
               logutil.error_client_name: [], #sys.stderr], # uncmnt to direct all errors to stderr
               logutil.combined_client_name : [formatfn(LOG_DIR_COMB, logutil.combined_client_name, dt)]}
    logutil.set_clients(clients)
    return (logutil, dt) 

def get_log() :
    logutil = getattr(g, '_logutil', None)
    if logutil is None :
        (logutil, dt) = init_logutil()
    return logutil


def get_db_args() :
    logutil = get_log()
    dbargs = CONFIG['dbargs']
    dbargs['logutil'] = logutil
    dbargs['logclient'] = DB_LOG_CLIENT 
    return dbargs

def get_db() :
    dbutil = getattr(g, '_dbutil', None)
    if dbutil is None :
        dbargs = get_db_args()
        dbutil = g._dbutil = dbUtil(dbargs)
        dbutil.login()
        dbutil.use_database(SCHEMA['dbname'])
    return dbutil

def get_vm_args() :
    logutil = get_log()
    vmargs = CONFIG['vmargs']
    vmargs['logutil'] = logutil
    vmargs['logclient'] = VM_LOG_CLIENT 
    return vmargs

def get_vm() :
    vmutil = getattr(g, '_vmutil', None)
    if vmutil is None :
        vmargs = get_vm_args()
        vmutil = g._vmutil = vmUtil(vmargs)
        vmutil.login()
    return vmutil

def get_auth_args() :
    logutil = get_log()
    dbutil = get_db()
    authargs = {'dbutil' : dbutil, 'logutil' : logutil, 'logclient' : AUTH_LOG_CLIENT}
    return authargs

def get_auth() :
    authutil = getattr(g, '_authutil', None)
    if authutil is None:
        authargs = get_auth_args()
        authutil = g._authutil = authUtil(authargs) 
    return  authutil

def get_devops() :
    devopsutil = getattr(g, '_devopsutil', None)
    if devopsutil is None :
        logutil = get_log()
        dbargs = get_db_args()
        vmargs = get_vm_args()
        authargs = get_auth_args()
        devopsargs = CONFIG['devopsargs']
        devopsargs['logutil'] = logutil
        devopsargs['logclient'] = DEVOPS_LOG_CLIENT
        devopsargs['schema'] = SCHEMA

        rootkey = devopsargs['sshkey']
        pubkey_text = ""
        with open(rootkey['pubkey_file'], 'r+') as fh :
            pubkey_text = fh.read()
        rootkey['public_key'] = pubkey_text
        devopsargs['sshkey'] = rootkey
        devopsutil = devopsUtil(dbargs, vmargs, authargs, devopsargs)
    return devopsutil



def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def not_found(what) :
    return Response(
        'Could not find %s resource with given URL. \n'%str(what), 404,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def bad_args(what) :
    return Response(
        'This Endpoint was not called with the proper arguments.(%s)'%what, 400,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.values.get('token')
        if not auth :
            auth = request.json.get('token')
        authutil = get_auth()
        user = authutil.validate_token(auth)
        if not auth or not user :
            return authenticate()
        g._caller_id = user
        return f(*args, **kwargs)
    return decorated

def requires_root(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.values.get('token')
        if not auth :
            auth = request.json.get('token')
        authutil = get_auth()
        user = authutil.validate_token(auth)
        if not auth or not user :
            return authenticate()
        if not authutil.verify_auth_level(user, authutil.AUTH_ROOT) :
            return authenticate()
        g._caller_id = user
        return f(*args, **kwargs)
    return decorated


### Users Handling ###
@DEVOPS_HANDLER_APP.route('/users/<string:username>', methods=['GET'])
@requires_auth
def get_user(username):
    devopsutil = get_devops()
    user = devopsutil.get_user(username)
    if user :
        return jsonify(devopsutil.get_user(username))
    else :
        return not_found("user")



@DEVOPS_HANDLER_APP.route('/users/', methods=['POST'])
@requires_root
def create_user():
    devopsutil = get_devops()
    username = request.json.get('name')
    email = request.json.get('email')
    pwhash = devopsutil.hashpw(username, request.json.get('pwd'))
    auth = request.json.get('auth')
    token = devopsutil.create_user({'username' : username,
                                    'email' : email,
                                    'pwhash' : pwhash,
                                    'auth' : auth})
    return jsonify({'username' : username, 'email' : email})


### Token Handling ###

@DEVOPS_HANDLER_APP.route('/tokens/', methods=['POST'])
def get_token() :
    devopsutil = get_devops()
    authutil = devopsutil.authutil
    name = request.json.get('username')
    pwhash = devopsutil.hashpw(name, request.json.get('pwd'))
    if authutil.validate_user(name, pwhash) :
        tok = authutil.get_token(name)
        return jsonify({'name' : name, 'token' : str(tok)})
    else :
        return not_found("User Auth")




### Compute Handling ###
@DEVOPS_HANDLER_APP.route('/compute/<string:instance_id>', methods=['GET'])
@requires_auth
def get_instance(instance_id):
    devopsutil = get_devops()
    instance = devopsutil.get_vm_instances(instance_id)
    if instance :
        return jsonify(instance=instance[0])
    else :
        return not_found("Instance")


@DEVOPS_HANDLER_APP.route('/compute/', methods=['GET'])
@requires_auth
def get_instances():
    devopsutil = get_devops()
    username = request.values.get('username')
    instances = devopsutil.get_vm_instances()
    if instances :
        if username :
            return jsonify([inst for inst in instances if inst['creator'] == username])
        return jsonify(instances=[inst for inst in instances])
    else :
        return not_found("Instance(s)")


@DEVOPS_HANDLER_APP.route('/compute/', methods=['POST'])
@requires_auth
def create_instance() :
    devopsutil = get_devops()
    authutil = devopsutil.authutil
    caller = getattr(g, '_caller_id', None)
    inst_name = request.json.get('instance_name')
    image = request.json.get('image', IMAGE_DEFAULT)
    class_slug = request.json.get('class',  CLASS_SLUG_DEFAULT)

    provider = PROVIDER_DEFAULT 
    region = REGION_DEFAULT

    if not inst_name :
        return bad_args("Need to include Instance Name")

    instance = devopsutil.create_vm_instance(caller, {'name' : inst_name,
                                                      'image' : image,
                                                      'region' : region,
                                                      'class' : class_slug})
    if not instance :
        return bad_args("Instance Could not be Made Properly")
    instance = devopsutil.get_vm_instances(instance.id)
    return jsonify(instance=instance[0])



### Snapshot Handling ###


### SSHKey Handling ###


if __name__ == '__main__':
    global CONFIG
    global SCHEMA

    (logutil, dt) = init_logutil()
    logclient = HANDLER_LOG_CLIENT

    args = parse_args(sys.argv)
    if not args.config :
        self.logger.log_event(logclient, "HANDLER STARTUP", 'f', [], "", "No Config File Given")
        sys.exit(1)

    if not args.schemaf :
        self.logger.log_event(logclient, "HANDLER STARTUP", 'f', [], "", "No DB Schema File Given")
        sys.exit(1)

    CONFIG = load_json_file(args.config) 
    SCHEMA = load_json_file(args.schemaf)

    if not CONFIG:
        sys.stderr.write("Failed to parse input configuration file.")
        sys.exit(1)

    DEVOPS_HANDLER_APP.run(debug=True)


