#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

########################################################################################
#                                  Praxyk API Server                                   #
#  This is the main request handling code for the user-facing API server. It defines   #
#  exactly how to respond to all of the valid route requests that we recieve from      #
#  users. It depends on a series of util classes defined in /libs/, these abstract the #
#  process of authentication and user-data distribution out from the actual request    #
#  handling code.                                                                      #
#                                     Arguments                                        #
#  Use -h or --help to print script help                                               #
#                                                                                      #
#  See https://github.com/jhallard/Praxyk/wiki/Praxyk-API for complete API guide.      #
########################################################################################

import sys, os
import argparse
import datetime
import json

from __init__ import PRAXYK_API_APP

from libs.users_route import *
from models import *

from flask import Flask, jsonify, request, Response, g
from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

from functools import wraps

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


DESCRIPTION = """
##### Write a Description of this Script Here #####
"""

# @info - parse command line args into useable dictionary
#         right now we only take a config file as an argument
def parse_args(argv) :
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--metaconfig', help="Full path to the json file containing info " + \
                                             "about the meta-database for storing log files.")
    parser.add_argument('--local', action='store_true', help="Use this flag to run the server on " + \
                                                            "localhost:5000 instead of as a live server.")
    return parser.parse_args()


# @info - takes a given json file and loads it into an active dictionary for return
def load_json_file(fn) :
    if os.path.isfile(fn) :
        with open(fn, 'r+') as fh :
            data = json.load(fh)
        return data
    return None

PRAXYK_API_APP = Flask(__name__, static_url_path="")
api = Api(PRAXYK_API_APP)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


api.add_resource(UserRoute, '/users/<string:user_id>', endpoint='user')
api.add_resource(UsersRoute, '/users/', endpoint='users')


# @info - Main function, parse the inputs to see if the database needs to be either build or created
#         if so, build, fill and exit. IF not, then just run in a infinite loop waiting for requests to 
#         handle
if __name__ == '__main__':
    
    args = parse_args(sys.argv)
    # @info - you can do stuff here before the app actually starts running, like setup db connections
    #         or make sure other servers are active, etc.
    with PRAXYK_API_APP.app_context():
        pass

    # will run on localhost:5000 if --local flag is given
    if args.local :
        PRAXYK_API_APP.run(debug=True, threaded=True)
    # else we run a http server that can listen for foreign connections on port 5000
    else :
        http_server = HTTPServer(WSGIContainer(PRAXYK_API_APP))
        http_server.listen(5000)
        IOLoop.instance().start()



