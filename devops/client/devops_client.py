#!/usr/bin/python
import requests
import sys, os
import argparse
import datetime
import json

from os.path import expanduser

CONFIG_DIR = str(expanduser("~"))+'/.praxykdevops/client/config'

DESCRIPTION = """
This script is the client-side bindings for the Praxyk DevOps API. It uses the requests python
library to wrap around the exposed API and simplify the management of virtual machines and their
images on the command line.
All calls to the API must be done with tokens, to get a token, you must log in. The token will
remain valid for about 24 hours when it will then expire requiring you to log in again.
When you get a token by using the login function, the token will be saved in a json file in your home
directory. Do not touch this file for it is auto-managed by this script.
--- Argument Descriptions ---
Actions : Actions describe what you want to do, but not what you want to do the action to. For instance, if
you want to create an instance, you would call ./devops_util create instance. If you wanted to see all of the
existing snapshots, you would call ./devops_util get snapshots. Actions are also used to initialize a user (setup
sshkeys and change the default password) by calling ./devops_util setup. 
Nouns : Nouns describe what you want to apply the action to. Nouns to not have to be submitted if you are logging in
or you are setting-up the account, otherwise one must be given. Nouns can be {user, users, instance, instances, snapshot, snapshots}
"""

# @info - parse command line args into useable dictionary
#         right now we only take a config file as an argument
def parse_args(argv) :
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('action', help="This argument describes what action you want to take." +\
                                       "This can be one of the following : {setup, login, get, create, delete, update}.")
    parser.add_argument('noun',  nargs='?', default="", help="This argument describes what you want to apply the action to "+\
                                                        " and is not required if the action you submitted is 'login' or 'setup'." +\
                                                        "Can be one of : {user[s], instance[s], snapshot[s]}")
    return parser.parse_args()

# @info - grabs the user's current token and username from a local file and return it to be used.
def load_auth_info() :
    pass

# @info - walks a new user through the process of logging into their account, changing the
#         existing default password, getting their first token, and setting up their sshkey.
def setup_client() :
    pass


# @info - this logs the user into the API service by submitting their username and password in return for a temporary access
#         token. This token is stored in a hidden directory and can be loaded automatically when the user makes future requests.
def login_client() :
    pass



# @info - main function, has the sys.argv args parsed and performs a switch based on those arguments.
if __name__ == "__main__" :
    args = parse_args(sys.argv)

    if args.action == "setup" :
        return setup_client()

    if args.action = "login" :
        return login_client()

