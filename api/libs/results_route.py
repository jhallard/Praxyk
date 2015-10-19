#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines the results model and any models that are directly related

## Note - This model definition is shared across multiple servers and code branches, DO NOT
##        change this file unless you have permission or know exactly what you're doing. 


from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request, Response, g, url_for

from api import db, USER_ENDPOINT, TRANSACTIONS_ENDPOINT, RESULTS_ENDPOINT
from auth_route import *

DEFAULT_NUM_PAGES = 1
DEFAULT_PAGE_SIZE = 100
DEFAULT_START_PAGE=0
DEFAULT_PAGE=0


class ResultsRoute(Resource):

    def __init__(self):
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('pagination', type=bool, default=True, location='json')
        self.reqparse.add_argument('start_page', type=int, default=DEFAULT_START_PAGE, location='json')
        self.reqparse.add_argument('page', type=int, default=DEFAULT_PAGE, location='json')
        self.reqparse.add_argument('pages', type=int, default=DEFAULT_NUM_PAGES, location='json')
        self.reqparse.add_argument('page_size', type=int, default=DEFAULT_PAGE_SIZE, location='json')
        super(ResultsRoute, self).__init__()

    def get(self, trans_id):
        self.transaction_id = trans_id
        self.args = self.reqparse.parse_args()
        for value in self.args.values():
            if (value < 0):
                # @TODO throw an error
                abort(404)
        # @TODO add some logic to determine the next page (if there is one), and how to properly query the database for the right set of data
        next_url = ""
        if args['page']:
            next_url += "?page=%d" % args['page'] + 1
        if args['page_size']:
            next_url += "?page_size=%d" % args['page_size']
        if args['start_page']:
            if args['pages'] and args['pages'] < args['start_page']:
                # @TODO throw an error
                abort(404)
        # @TODO more logic to handle next_url redirection

        # @TODO add a database call to fill in the item data using the arguments as parameters so the data is properly paginated.
        res = {'code': 200, 'items' : [], 'next' : "api.praxyk.com/results/%d/%s" % (self.transaction_id, next_url)}

        return jsonify(res)
