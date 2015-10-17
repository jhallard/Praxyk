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

from flask import Flask, jsonify, request, Response, g
from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

from functools import wraps

from api import models
from models import user, transaction

user_fields = {
    'name' : fields.String,
    'email' : fields.String,
    'id' : fields.String,
    'uri' : fields.Url(USER_ENDPOINT)
    'transactions_url' : fields.String
}

# @info - class with routes that contain a user id 
# ie `GET api.praxyk.com/users/12345`
class UserRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        super(UserRoute, self).__init__()

    @marshall_with(user_fields, envelope='user')
    def get(user_id) :
        return User.get(user_id)

    @marshall_with(user_fields, envelope='user')
    def put(user_id) :
        pass

    def delete(user_id) :
        pass



# @info - class with routes that don't contain a user id 
# ie `POST api.praxyk.com/users/`
class UsersRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        super(UsersRoute, self).__init__()

    def post() :
        args = self.reqparse.parse_args()

        pass
    




