#!/bin/python2

# @info - This file will run the various unit tests for this server module. The specific set
#         of tests run depends on the input arguments, see the help section for more info.

import _fix_path_

from server_tests import *
from auth_unit_tests import *
from vm_unit_tests import *
from db_unit_tests import *
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
LOG_DIR_TEST = BASEDIR + "test-logs/"


## logutil client names
VM_LOG_CLIENT = 'vm_client'
DB_LOG_CLIENT = 'db_client'
AUTH_LOG_CLIENT = 'auth_client'
SERVER_LOG_CLIENT = 'server_client'
VM_TEST_LOG_CLIENT = 'vm_test_client'
DB_TEST_LOG_CLIENT =  'db_test_client'
AUTH_TEST_LOG_CLIENT  ='auth_test_client'
SERVER_TEST_LOG_CLIENT = 'server_test_client'


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
    parser.add_argument('--schemaf', help="Full path to the .schema file for a database. This is required if " \
                                          "you are testing the datbase, auth, or server.")
    parser.add_argument('config', help="Full path to the config file for this regression. It should include " + \
                                       "the vm tokens, dbip, dbpw, and dbuser.")
    parser.add_argument('test', help="Which test do you want to run. The following are accepted : " + \
                                     "{vmtest, authtest, servertest, dbtest}")
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
               VM_LOG_CLIENT            : [formatfn(LOG_DIR_VM, VM_LOG_CLIENT, dt)],
               DB_LOG_CLIENT            : [formatfn(LOG_DIR_DB, DB_LOG_CLIENT, dt)],
               AUTH_LOG_CLIENT          : [formatfn(LOG_DIR_AUTH, AUTH_LOG_CLIENT, dt)],
               SERVER_LOG_CLIENT        : [formatfn(LOG_DIR_SERVER, SERVER_LOG_CLIENT, dt)],
               VM_TEST_LOG_CLIENT       : [sys.stdout, formatfn(LOG_DIR_TEST, VM_TEST_LOG_CLIENT, dt)],
               AUTH_TEST_LOG_CLIENT     : [sys.stdout, formatfn(LOG_DIR_TEST, AUTH_TEST_LOG_CLIENT, dt)],
               SERVER_TEST_LOG_CLIENT   : [sys.stdout, formatfn(LOG_DIR_TEST, SERVER_TEST_LOG_CLIENT, dt)],
               DB_TEST_LOG_CLIENT       : [sys.stdout, formatfn(LOG_DIR_TEST, DB_TEST_LOG_CLIENT, dt)],
               logutil.error_client_name: [],#[sys.stderr], # uncmnt to direct all errors to stderr
               logutil.combined_client_name : [formatfn(LOG_DIR_COMB, logutil.combined_client_name, dt)]}
    logutil.set_clients(clients)
    return (logutil, dt) 

# call vmUnitTest().run()
def vm_unittest(globalargs, testargs) :
    vmargs = globalargs['vmargs'] 
    vmargs['logclient'] = VM_LOG_CLIENT
    vmargs['logutil'] = testargs['logutil']
    test = vmUnitTest(vmargs, testargs)
    return test.run()


# call authUnitTest().run()
def auth_unittest() :
    pass

# call serverUnitTest().run()
def server_unittest() :
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
            'dbtest' : db_unittest}
    TESTCLIENTS = {
            'vmtest' : VM_TEST_LOG_CLIENT,
            'authtest' : AUTH_TEST_LOG_CLIENT,
            'servertest' : SERVER_TEST_LOG_CLIENT,
            'dbtest' : DB_TEST_LOG_CLIENT}

    DBSCHEMA = None # used only for db, auth, and server tests.

    args = parse_args(sys.argv)
    (logutil, db) = init_logutil()
    arg_map = parse_config_file(args.config) 

    if args.schemaf :
        with open(args.schemaf) as fh :
            DBSCHEMA = json.load(fh)

    if not arg_map:
        sys.stderr.write("Failed to parse input configuration file.")
        sys.exit(1)

    testname = args.test

    if testname not in TESTS.keys() :
        errmsg = "Invalid input for option test. Must be one of (%s)." + \
                 "Try with '-h' option to see help"
        sys.stderr.write(errmsg % str(TESTS))
        sys.exit(1)

    testargs = {'logutil'   : logutil,
                'logclient' : TESTCLIENTS[testname],
                'schema'    : DBSCHEMA}

    test_fn = TESTS[testname]

    result = test_fn(arg_map, testargs)

    sys.exit(0 if result else 1)
    
