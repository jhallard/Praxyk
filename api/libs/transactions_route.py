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
from flask import Flask, jsonify, abort, make_response, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with, inputs
from flask.ext.httpauth import HTTPBasicAuth

from functools import wraps

from api import db, USER_ENDPOINT, USERS_ENDPOINT, TRANSACTION_ENDPOINT, TRANSACTIONS_ENDPOINT
from api import Transaction

from auth_route import *
from libs.route_fields import *

DEFAULT_PAGE_SIZE = 100
DEFAULT_PAGE=1


# @info - class with routes that contain a transaction id 
# ie `GET api.praxyk.com/transactions/12345`
class TransactionRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(TransactionRoute, self).__init__()

    @requires_auth
    def get(self, id) :
        try :
            trans = Transaction.query.get(id)
            if not trans :
                abort(404)
            caller = g._caller
            if not caller or not validate_owner(caller, trans.user_id) :
                abort(404)
            return jsonify( {"code" : 200, "transaction" : marshal(trans, transaction_fields)} )
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)


    # this should be changed to a put route with a cancel boolean value passed in to allow
    # the user to cancel an active transaction
    @requires_auth
    def delete(id) :
        try : 
            # @TODO - Stop Transaction From Happening if it's active still
            pass
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)



# @info - Route class for /transactions/, only has `GET` defined. Users can get all of their transaction history
#         here with the ?user_id=$USER_ID parameter or api-admins can get any transactions from any user. 
#         transactions can be filtered by api-version, model, and/or service.
class TransactionsRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id',      type=int, default=None, required=False, location=['json', 'values'])
        self.reqparse.add_argument('reverse_sort', type=inputs.boolean, default=False, required=False, location=['json', 'values'])
        self.reqparse.add_argument('service',      type=str, default=None, required=False, location=['json', 'values'])
        self.reqparse.add_argument('model',        type=str, default=None, required=False, location=['json', 'values'])
        self.reqparse.add_argument('version',      type=str, default=None, required=False, location=['json', 'values'])
        self.reqparse.add_argument('limit',        type=int, default=None, required=False, location=['json', 'values'])
        self.reqparse.add_argument('pagination',   type=inputs.boolean,  default=True, location=['json', 'values', 'headers'])
        self.reqparse.add_argument('page',         type=int, default=DEFAULT_PAGE, location=['json', 'values'])
        self.reqparse.add_argument('page_size',    type=int, default=DEFAULT_PAGE_SIZE, location=['json', 'values'])
        super(TransactionsRoute, self).__init__()

    @requires_auth
    def get(self) :
        try :
            args = self.reqparse.parse_args()
            user_id = args.get('user_id', -1)
            caller = g._caller
            print str(args)

            if not caller or not validate_owner(caller, user_id) :
                abort(404)

            user_name = User.query.get(user_id).name if user_id else "All"

            if not args.page : args.page = DEFAULT_PAGE
            if not args.page_size : args.page_size = DEFAULT_PAGE_SIZE

            transactions=[]
            if user_id > 0 :
                transactions  =  Transaction.query.filter_by(user_id=user_id)
            else :
                transactions  =  Transaction.query

            if args.reverse_sort :
                transactions  =  transactions.order_by(Transaction.id.desc())
            else :
                transactions  =  transactions.order_by(Transaction.id)
            
            if not transactions :
                abort(404)
            
            if args.service :
                transactions = transactions.filter_by(service=args.service)
            
            if args.model :
                transactions = transactions.filter_by(model=args.model)

            # if not pagination dump all results
            if not args.pagination :	
                if args.limit and args.limit > 0 :
                    transactions = transactions.limit(args.limit)
                else :
                    transactions = transactions.all()
                transactions = [marshal(trans, transaction_fields) for trans in transactions]
                return jsonify({"code" : 200, 'user_name' : user_name, 'transactions' : transactions})
            
            page = {}

            page_results  = self.get_page_from_results(transactions, args.page, args.page_size)

            page_json = page_results['results_json']
            next_page_num = page_results['next_page_num']
            prev_page_num = page_results['prev_page_num']
            last_page_num = page_results['last_page_num']
            if page_json : 
                page = {"page_number" : args.page,
                        "transactions"     : page_json}
                                                                                                                                                         
            next_page = "" if not next_page_num else url_for(TRANSACTIONS_ENDPOINT,
                                                             page_size=args.page_size,
                                                             page=next_page_num,
                                                             _external=True)
            prev_page = "" if not prev_page_num else url_for(TRANSACTIONS_ENDPOINT,
                                                             page_size=args.page_size,
                                                             page=prev_page_num,
                                                             _external=True)

            first_page = url_for(TRANSACTIONS_ENDPOINT, page_size=args.page_size, page=1, _external=True)
            last_page = url_for(TRANSACTIONS_ENDPOINT, page_size=args.page_size, page=last_page_num, _external=True)


            return {"code"        : 200,
                    "page"        : page,
                    "next_page"   : next_page,
                    "prev_page"   : prev_page,
                    "first_page"  : first_page,
                    "last_page"   : last_page} 

        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)


    # takes a list of results, a page number, and a page_size to find the index bounds
    # on the page and returns the page as a list of results
    # returns (result_list, next_page_num, last_page_num) where next_page_num is None if result_list contains
    # results of the last page
    def get_page_from_results(self, result_list, page, page_size) :
        startind = (page-1)*page_size
        endind = (page)*page_size
        amount = result_list.count()
        last_page_num = (amount/page_size) + 1

        if startind < 0 or startind > amount :
            return (None, None)
        if endind < 0 :                                                                                                                              
            return (None, None)

        # results_subset = result_list.filter(Transaction.id >= startind).filter(Transaction.id < endind).all()
        # results_subset = result_list.filter(Transaction.id >= startind).filter(Transaction.id < endind).all()


        results_json = []
        temp_list = result_list.all()
        results_subset = temp_list[startind:endind] if startind > 0 else temp_list[:endind]
        print str(results_subset) + "  " + str(result_list)
        for result in results_subset :
            results_json.append(marshal(result, transaction_fields))

        res = {'results_json' : results_json,
               'next_page_num' : (None if endind >= result_list.count() else page+1),
               'prev_page_num' : (None if page == 1 else page-1),
               'last_page_num' : last_page_num}

        return res

    




