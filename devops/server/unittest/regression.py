#!/bin/python2

# @info - This file will run the various unit tests for this server module. The specific set
#         of tests run depends on the input arguments, see the help section for more info.

import _fix_path_

from server_tests import *
from auth_util_tests import *
from vm_util_tests import *
from log_util import *

import sys, os
import argparse
import datetime
import json

## logging directories
BASEDIR = "../logs/"
LOG_DIR_VM = BASEDIR + "vm-logs"
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


def formatfn(logdir, client, dt) :
    dt = dt.replace(" ", "_")
    return logdir+client+'_'+dt +'.log'

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
               logutil.error_client_name: [],#[sys.stderr],
               logutil.combined_client_name : [formatfn(LOG_DIR_COMB, logutil.combined_client_name, dt)]}
    logutil.set_clients(clients)
    return (logutil, dt) 

# call vmUnitTest().run()
def vm_unittest(globalargs, testargs) :
    vmargs = globalargs['vmargs'] 
    vmargs['logclient'] = VM_LOG_CLIENT
    vmargs['logutil'] = testargs['logutil']
    tst = vmUnitTest(vmargs, testargs)
    return tst.run()


# call authUnitTest().run()
def auth_unittest() :
    pass

# call serverUnitTest().run()
def server_unittest() :
    pass

# call dbUnitTest().run()
def db_unittest() :
    pass

# @info - calls the various unit tests after configuring them to the users specifications.
if __name__ == "__main__" :

    # all of the possible tests that can be run from the command line
    TESTS = {'vmtest' : vm_unittest,
            'authtest' : auth_unittest,
            'servertest' : server_unittest,
            'dbtest' : db_unittest}
    TESTCLIENTS = {
            'vmtest' : VM_TEST_LOG_CLIENT,
            'authtest' : AUTH_TEST_LOG_CLIENT,
            'servertest' : SERVER_TEST_LOG_CLIENT,
            'dbtest' : DB_TEST_LOG_CLIENT}

    args = parse_args(sys.argv)
    (logutil, db) = init_logutil()
    arg_map = parse_config_file(args.config) 

    if not arg_map:
        sys.stderr.write("Failed to parse input configuration file.")
        sys.exit(1)

    test = args.test

    if test not in TESTS.keys() :
        sys.stderr.write("Invalid input for option test. Must be one of (%s)" % tests)
        sys.exit(1)

    test_fn = TESTS[test]
    testargs = {'logutil' : logutil,
                'logclient' : TESTCLIENTS[test]
                }

    result = test_fn(arg_map, testargs)

    sys.exit(0 if result else 1)
    
