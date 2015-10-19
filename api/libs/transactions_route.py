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

from api import db, USER_ENDPOINT, USERS_ENDPOINT, TRANSACTION_ENDPOINT
from api import Transaction

from auth_route import *

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
    'user_url' : fields.String,
    'status' : fields.String,
    'uploads_total' : fields.Integer,
    'uploads_success' : fields.Integer,
    'uploads_failed' : fields.Integer,
    'size_total_KB' : fields.Float,
    'created_at' : fields.DateTime(dt_format='iso8601'), #'rfc822'),
    'finished_at' : fields.DateTime(dt_format='iso8601'), #'rfc822'),
    'uri' : fields.Url(TRANSACTION_ENDPOINT, absolute=True)
}

transactions_fields = {
    'transactions' : fields.Nested(transaction_fields),
    'user_id' : fields.Integer
}

# @info - class with routes that contain a transaction id 
# ie `GET api.praxyk.com/transactions/12345`
class TransactionRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(TransactionRoute, self).__init__()

    @marshal_with(transaction_fields, envelope='transaction')
    @requires_auth
    def get(self, id) :
        try :
            trans = Transaction.query.get(id)
            if not trans :
                abort(404)
            caller = g._caller
            if not caller or not validate_owner(caller, trans.user_id) :
                abort(404)
            return trans
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

    def delete(id) :
        try : 
            # @TODO - Stop Transaction From Happening if it's active still
            pass
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)



# @info - class with routes that don't contain a user id 
# ie `POST api.praxyk.com/users/`
class TransactionsRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=int, required=False, default=None, location='json')
        self.reqparse.add_argument('pagination', type=bool, default=True, location='json')
        self.reqparse.add_argument('start_page', type=int, default=DEFAULT_START_PAGE, location='json')
        self.reqparse.add_argument('page', type=int, default=DEFAULT_PAGE, location='json')
        self.reqparse.add_argument('pages', type=int, default=DEFAULT_NUM_PAGES, location='json')
        self.reqparse.add_argument('page_size', type=int, default=DEFAULT_PAGE_SIZE, location='json')
        super(TransactionsRoute, self).__init__()

    # @marshal_with(transactions_fields, envelope='transactions')
    @requires_auth
    def get(self) :
        try :
            args = self.reqparse.parse_args()
            user_id = args.get('user_id', -1)
            caller = g._caller
            if not caller or not validate_owner(caller, user_id) :
                abort(404)

            user_name = User.query.get(user_id) if user_id else "All"

            if user_id > 0 :
                transactions  =  Transaction.query.filter_by(user_id=user_id)
            else :
                transactions  =  Transaction.query.order_by(Transaction.created_at)
                
            if not transactions :
                abort(404)
            transactions = [marshal(trans, transaction_fields) for trans in transactions]
            return jsonify({'user_name' : user_name, 'transactions' : transactions})
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)
    




