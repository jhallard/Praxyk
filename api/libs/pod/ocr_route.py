#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /users/ route for the Praxyk API.
##         This involved creating a class with the PUT, GET, POST, and 
##         DELETE methods defined. Once defined, the main API handler 
##         (../api_server.py) can simply import this class and use it to 
##         handle any user-related requests.

import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify, request, Response, g, abort, make_response, render_template, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with

from api import db, USER_ENDPOINT, USERS_ENDPOINT, CONFIRM_ENDPOINT, POD_ENDPOINT, POD_OCR_ENDPOINT, RESULTS_ENDPOINT
from api import User, Role, user_datastore, mail, redis

from libs.auth_route import *
from libs.transactions_route import *

# @info - class with routes that contain a user id 
# ie `GET api.praxyk.com/users/12345`
class POD_OCR_Route(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(POD_OCR_Route, self).__init__()

    @marshal_with(transaction_fields, envelope='transaction')
    @requires_auth
    def post(self) :
        try :
            caller = g._caller
            if not caller :
                abort(404)

            command_url = url_for(POD_OCR_ENDPOINT)
            new_trans = Transaction(user_id=caller.id, command_url=command_url)
            caller.transactions.append(new_trans)
            db.session.commit()

            return new_trans
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

