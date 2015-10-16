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

from libs import *
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
    # @TODO add relevant command line args here
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--metaconfig', help="Full path to the json file containing info " + \
                                             "about the meta-database for storing log files.")
    parser.add_argument('--local', action='store_true', help="Use this flag to run the server on " + \
                                                            "localhost:5000 instead of as a live server.")
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

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return {'tasks': [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': True}


api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')


# @info - Main function, parse the inputs to see if the database needs to be either build or created
#         if so, build, fill and exit. IF not, then just run in a infinite loop waiting for requests to 
#         handle
if __name__ == '__main__':
    global CONFIG
    global SCHEMA

    # (logutil, dt) = init_logutil()
    # logclient = HANDLER_LOG_CLIENT

    args = parse_args(sys.argv)
    if not args.config :
        # self.logger.log_event(logclient, "HANDLER STARTUP", 'f', [], "", "No Config File Given")
        sys.exit(1)

    if not args.schemaf :
        # self.logger.log_event(logclient, "HANDLER STARTUP", 'f', [], "", "No DB Schema File Given")
        sys.exit(1)

    CONFIG = load_json_file(args.config) 
    SCHEMA = load_json_file(args.schemaf)

    if not CONFIG:
        sys.stderr.write("Failed to parse input configuration file.\n")
        sys.exit(1)

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



