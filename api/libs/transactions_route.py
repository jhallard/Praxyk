#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /transactions/ route for the Praxyk API.

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
from api import Transaction
# from models.sql.transaction import Transaction

DEFAULT_NUM_PAGES = 1
DEFAULT_PAGE_SIZE = 100
DEFAULT_START_PAGE=0
DEFAULT_PAGE=0


transaction_fields = {
    'trans_id' : fields.String(attribute="id"),
    'user_id' : fields.Integer,
    'command_url' : fields.String,
    'data_url' : fields.String,
    'results_url' : fields.String,
    'status' : fields.String,
    'created_at' : fields.DateTime(dt_format='rfc822'),
    'uri' : fields.Url(USER_ENDPOINT, absolute=True)
}

transactions_fields = {
    'transactions' : fields.Nested(transaction_fields),
    'user_id' : fields.Integer
}

# @info - class with routes that contain a transaction id 
# ie `GET api.praxyk.com/transactions/12345`
class TransactionRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        super(TransactionRoute, self).__init__()

    @marshal_with(transaction_fields, envelope='user')
    def get(self, id) :
        trans =  Transaction.query.get(id)
        if not trans :
            abort(404)
        return trans

    @marshal_with(transaction_fields, envelope='user')
    def put(self, id) :
        args = self.reqparse.parse_args()
        user = User.query.get(id)

        if not user :
            abort(404)

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
class TransactionsRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse.add_argument('user_id', type=int, required=True, location='json')
        self.reqparse.add_argument('pagination', type=bool, default=True, location='json')
        self.reqparse.add_argument('start_page', type=int, default=DEFAULT_START_PAGE, location='json')
        self.reqparse.add_argument('page', type=int, default=DEFAULT_PAGE, location='json')
        self.reqparse.add_argument('pages', type=int, default=DEFAULT_NUM_PAGES, location='json')
        self.reqparse.add_argument('page_size', type=int, default=DEFAULT_PAGE_SIZE, location='json')
        super(TransactionsRoute, self).__init__()

    @marshal_with(transaction_fields, envelope='user')
    def post(self) :
        args = self.reqparse.parse_args()
        new_trans = Transaction
        if not new_trans :
            abort(403)

        db.session.add(new_user)
        db.session.commit()
        return new_user
    




