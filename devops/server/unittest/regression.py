#!/usr/bin/python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

# @info - This file will run the various unit tests for this server module. The specific set
#         of tests run depends on the input arguments, see the help section for more info.

import _fix_path_

from server_unit_tests import *
from auth_unit_tests import *
from vm_unit_tests import *
from db_unit_tests import *
from devops_unit_tests import *
from log_util import *

import sys, os
import argparse
import datetime
import json

## logging directories
BASEDIR = "../logs/"
LOG_DIR_VM = BASEDIR + "vm-logs/"
LOG_DIR_DB = BASEDIR + "db-logs/"
LOG_DIR_SERVER = BASEDIR + 'server-logs'
LOG_DIR_COMB = BASEDIR + "comb-logs/"
LOG_DIR_AUTH = BASEDIR + "auth-logs/"
LOG_DIR_DEVOPS = BASEDIR + "devops-logs/"
LOG_DIR_TEST = BASEDIR + "test-logs/"


## logutil client names
VM_LOG_CLIENT = 'vmclient'
DB_LOG_CLIENT = 'dbclient'
AUTH_LOG_CLIENT = 'authclient'
SERVER_LOG_CLIENT = 'serverclnt'
DEVOPS_LOG_CLIENT = 'devopsclnt'

VM_TEST_LOG_CLIENT = 'vmtestclnt'
DB_TEST_LOG_CLIENT =  'dbtestclnt'
AUTH_TEST_LOG_CLIENT  ='athtstclnt'
SERVER_TEST_LOG_CLIENT = 'srvrtstclnt'
DEVOPS_TEST_LOG_CLIENT = 'dvpststclnt'


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
                                        "vmtest flags     : [a b c d e f g] each one runs another series of tests."+\
                                        "devopstest flags : [a b c] ")
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
               VM_TEST_LOG_CLIENT       : [sys.stdout, formatfn(LOG_DIR_TEST, VM_TEST_LOG_CLIENT, dt)],
               AUTH_TEST_LOG_CLIENT     : [sys.stdout, formatfn(LOG_DIR_TEST, AUTH_TEST_LOG_CLIENT, dt)],
               SERVER_TEST_LOG_CLIENT   : [sys.stdout, formatfn(LOG_DIR_TEST, SERVER_TEST_LOG_CLIENT, dt)],
               DB_TEST_LOG_CLIENT       : [sys.stdout, formatfn(LOG_DIR_TEST, DB_TEST_LOG_CLIENT, dt)],
               DEVOPS_TEST_LOG_CLIENT   : [sys.stdout, formatfn(LOG_DIR_TEST, SERVER_TEST_LOG_CLIENT, dt)],
               logutil.error_client_name: [],#[sys.stderr], # uncmnt to direct all errors to stderr
               logutil.combined_client_name : [formatfn(LOG_DIR_COMB, logutil.combined_client_name, dt)]}
    logutil.set_clients(clients)
    return (logutil, dt) 

# call vmUnitTest().run()
def vm_unittest(globalargs, testargs) :
    vmargs = globalargs['vmargs'] 
    vmargs['logclient'] = VM_LOG_CLIENT
    vmargs['logutil'] = testargs['logutil']

    key = globalargs['devopsargs']['sshkey']
    pubkey_text = ""
    with open(key['pubkey_file'], 'r+') as fh :
        pubkey_text = fh.read()

    key['public_key'] = pubkey_text
    vmargs['sshkey'] = key
    test = vmUnitTest(vmargs, testargs)
    return test.run()


# call authUnitTest().run()
def auth_unittest(globalargs, testargs) :
    vmargs = globalargs['vmargs']
    vmargs['logclient'] = VM_LOG_CLIENT
    vmargs['logutil'] = testargs['logutil']

    dbargs = globalargs['dbargs']
    dbargs['dbip'] = dbargs['dbipv4']
    dbargs['logutil'] = testargs['logutil']
    dbargs['logclient'] = DB_LOG_CLIENT
    dbutil = dbUtil(dbargs)

    if not dbutil :
        sys.stderr.write("Could not init dbUtil, Exiting.")
        return False
    dbutil.login()

    authargs = {}
    authargs['dbutil'] = dbutil
    authargs['logclient'] = AUTH_LOG_CLIENT
    authargs['logutil'] = logutil

    test = authUnitTest(vmargs, authargs, testargs)
    return test.run()

# call serverUnitTest().run()
def server_unittest(globalargs, testargs) :
    return True
    pass


# call devopsUnitTest().run()
def devops_unittest(globalargs, testargs) :
    vmargs = globalargs['vmargs']
    vmargs['logclient'] = VM_LOG_CLIENT
    vmargs['logutil'] = testargs['logutil']

    dbargs = globalargs['dbargs']
    dbargs['dbip'] = dbargs['dbipv4']
    dbargs['logutil'] = testargs['logutil']
    dbargs['logclient'] = DB_LOG_CLIENT
    dbutil = dbUtil(dbargs)

    authargs = {}
    authargs['dbutil'] = dbutil
    authargs['logclient'] = AUTH_LOG_CLIENT
    authargs['logutil'] = logutil

    devopsargs = globalargs['devopsargs']
    devopsargs['schema'] = testargs['schema']
    devopsargs['logutil'] = logutil
    devopsargs['logclient'] = DEVOPS_LOG_CLIENT
    rootkey = devopsargs['sshkey']
    pubkey_text = ""
    with open(rootkey['pubkey_file'], 'r+') as fh :
        pubkey_text = fh.read()
    rootkey['public_key'] = pubkey_text
    devopsargs['sshkey'] = rootkey

    test = devopsUnitTest(dbargs, vmargs, authargs, devopsargs, testargs)
    return test.run()

    pass

# call dbUnitTest().run()
def db_unittest(globalargs, testargs) :
    dbargs = globalargs['dbargs']
    dbargs['dbip'] = dbargs['dbipv4']
    dbargs['logutil'] = testargs['logutil']
    dbargs['logclient'] = DB_LOG_CLIENT

    testargs['testtable'] = 'TEST_BUFFER'
            
    test = dbUnitTest(dbargs, testargs)
    return test.run()

##### Main Function #####
# @info - calls the various unit tests after configuring them to the users specifications.
if __name__ == "__main__" :

    # all of the possible tests that can be run from the command line
    # map the test argument to a test function above
    TESTS = {'vmtest' : vm_unittest,
            'authtest' : auth_unittest,
            'servertest' : server_unittest,
            'devopstest' : devops_unittest,
            'dbtest' : db_unittest}
    # map a test name to its client name
    TESTCLIENTS = {
            'vmtest' : VM_TEST_LOG_CLIENT,
            'authtest' : AUTH_TEST_LOG_CLIENT,
            'servertest' : SERVER_TEST_LOG_CLIENT,
            'devopstest' : DEVOPS_TEST_LOG_CLIENT,
            'dbtest' : DB_TEST_LOG_CLIENT}

    DBSCHEMA = None # used only for db, auth, devops, and server tests.
                    # set below if used.

    TESTFLAGS = None # set if they passed in the --flags arg followed by a string

    args = parse_args(sys.argv)
    arg_map = parse_config_file(args.config) 
    (logutil, db) = init_logutil()

    if not arg_map:
        sys.stderr.write("Failed to parse input configuration file.")
        sys.exit(1)

    testname = args.test

    if testname not in TESTS.keys() :
        errmsg = "Invalid input for option test. Must be one of (%s)." + \
                 "Try with '-h' option to see help"
        sys.stderr.write(errmsg % str(TESTS.keys()))
        sys.exit(1)

    # certain tests require a .schema file to be given with the --schemaf flag so
    # they can build a test database.
    if testname in ['dbtest', 'authtest', 'devopstest', 'servertest'] and not args.schemaf :
        errmsg = "Test [%s] requires the use of --schemaf flag and an accompanying" + \
                 "full path the a test db .schema file. Try with '-h' to see help"
        sys.stderr.write(errmsg % str(testname))
        sys.exit(1)

    if args.schemaf :
        with open(args.schemaf) as fh :
            DBSCHEMA = json.load(fh)

    if args.flags :
        TESTFLAGS = args.flags

    testargs = {'logutil'   : logutil,
                'logclient' : TESTCLIENTS[testname],
                'schema'    : DBSCHEMA,
                'flags'     : TESTFLAGS}

    test_fn = TESTS[testname]

    result = test_fn(arg_map, testargs)

    sys.exit(0 if result else 1)
    
