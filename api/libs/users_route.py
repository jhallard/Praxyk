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
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
from flask.ext.httpauth import HTTPBasicAuth

from functools import wraps

from api import db, USER_ENDPOINT, USERS_ENDPOINT
from models.sql.user import User


user_fields = {
    'name' : fields.String,
    'email' : fields.String,
    'user_id' : fields.String(attribute="id"),
    'uri' : fields.Url(USER_ENDPOINT, absolute=True),
    'transactions_url' : fields.String
}

# @info - class with routes that contain a user id 
# ie `GET api.praxyk.com/users/12345`
class UserRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=False, location='json')
        self.reqparse.add_argument('password', type=str, required=False, location='json')
        self.reqparse.add_argument('name', type=str, required=False, location='json')
        super(UserRoute, self).__init__()

    @marshal_with(user_fields, envelope='user')
    def get(self, id) :
        user =  User.query.get(id)
        if not user :
            abort(403)
        return user

    @marshal_with(user_fields, envelope='user')
    def put(self, id) :
        args = self.reqparse.parse_args()
        user = User.query.get(id)

        if not user :
            abort(403)

        if args['email'] :
            user.email = args['email']
        if args['password'] :
            user.pwhash = user.hashpw(args['password'])

        db.session.add(user)
        db.session.commit()
        return user


    def delete(id) :
        pass



# @info - class with routes that don't contain a user id 
# ie `POST api.praxyk.com/users/`
class UsersRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, location='json')
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        super(UsersRoute, self).__init__()

    @marshal_with(user_fields, envelope='user')
    def post(self) :
        args = self.reqparse.parse_args()
        new_user = User(name=args.name, email=args.email, password=args.password)
        if not new_user :
            abort(403)

        db.session.add(new_user)
        db.session.commit()
        return new_user
    




