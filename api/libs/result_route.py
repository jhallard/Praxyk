#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## Note - This model definition is shared across multiple servers and code branches, DO NOT
##        change this file unless you have permission or know exactly what you're doing. 


from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request, Response, g, url_for

from api import db, USER_ENDPOINT, TRANSACTIONS_ENDPOINT, RESULTS_ENDPOINT
from api import *
from auth_route import *

from models.nosql.pod.result_pod_ocr import *
from models.nosql.result_base import *

from libs.transactions_route import transaction_fields

DEFAULT_NUM_PAGES = 1
DEFAULT_PAGE_SIZE = 100
DEFAULT_START_PAGE=0
# DEFAULT_PAGE=0

def convert_timestr(dt) :
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def marshal_result(res) :
    return { "item_number"   : res.item_number,
             "item_name"     : res.item_name,
             "status"        : res.status,
             "size_KB"       : res.size_KB,
             "finished_at"   : convert_timestr(res.finished_at),
             "created_at"    : convert_timestr(res.created_at),
             "uri"           : url_for(RESULT_ENDPOINT, id=res.transaction_id, page_size=1, page=res.item_number),
             "result_string" : res.result_string }


# @info - this class defines the /results/<int:id> route, which allows user's to access all results for a
#         specific transaction given by @id. If a user wants to grab their results history across multiple
#         transactions, then can `GET /results/?user_id=<int:id>`
class ResultRoute(Resource):

    def __init__(self):
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('pagination', type=bool, default=True, location=['values', 'headers', 'json'])
        self.reqparse.add_argument('start_page', type=int, default=None, location=['values', 'json'])
        self.reqparse.add_argument('page', type=int, default=None, location=['values', 'json'])
        self.reqparse.add_argument('pages', type=int, default=None, location=['values', 'json'])
        self.reqparse.add_argument('page_size', type=int, default=DEFAULT_PAGE_SIZE, location=['values', 'json'])
        super(ResultRoute, self).__init__()

    # @info - takes a command_url string (from a transaction db.Model object), that looks like /v1/pod/ocr/
    #         and returns the tuple (pod, ocr) which represents the service being accessed (prediction on
    #         demand) and the model being accessed from that service (ocular character recognition).
    def get_service(self, transaction) :
        if transaction and transaction.command_url and len(transaction.command_url.split("/")) >= 3 :
            command_split =  transaction.command_url.split("/")
            return (command_split[2], command_split[3]) # returns ({pod|tlp}, {ocr, bayes_spam})

    # @info - This handles all get requests for requests grouped under a specific transaction, aka this handles
    #         all requests of type `/results/:trans_id`. The results are paginated by default, this can be turned 
    #         of by giving ?pagination=False which will cause all results to be dumped in a single list.
    @requires_auth
    def get(self, id):
        caller = g._caller
        trans = Transaction.query.get(id)
        if not trans or not caller or not validate_owner(caller, trans.user_id) :
            abort(404)

        (service, model) = self.get_service(trans)
        results = {}

        if service == SERVICE_POD :
            if model == MODELS_POD_OCR :
                results = self.get_results_pod_ocr(caller, trans)
            elif model == MODELS_POD_BAYES_SPAM :
                results = {}
        elif service == SERVICE_TLP : 
            results = {}

        return jsonify(results)

    def get_results_pod_ocr(self, caller, trans) :
        args = self.reqparse.parse_args()
        print str(args)

        result_list = Result_POD_OCR.query.filter(transaction_id=trans.id).execute()
        if not result_list and len(result_list) != trans.uploads_total :
            print "\n\n Not All Result Recovered from Redis DB" + str(result_list) + "\n\n"

        print str(result_list)

        if not args.pagination :
            results_json = []
            for res in result_list :
                results_json.append(marshal_result(res))
            return {"code" : 200, "transaction" : marshal(trans, transaction_fields), "results" : results_json } 

        # if they give nothing return page 1
        if not args.page and not args.pages and not args.start_page :
            args.page = 1

        # if not args.page and not args.start_page :
            # args

        if args.page :
            (page_json, next_page_num) = self.get_page_from_results(result_list, args.page, args.page_size)
            if not page_json :
                abort(404)
            next_page = "" if not next_page_num else url_for(RESULT_ENDPOINT,
                                                             id=trans.id,
                                                             page_size=args.page_size,
                                                             page=next_page_num)
            return {"code"        : 200,
                    "transaction" : marshal(trans, transaction_fields),
                    "pages"       : {args.page : page_json},
                    "next_page"   : next_page }
            


    # takes a list of results, a page number, and a page_size to find the index bounds
    # on the page and returns the page as a list of results
    # returns (result_list, next_page_num) where next_page_num is None if result_list contains
    # results of the last page
    def get_page_from_results(self, result_list, page, page_size) :
        startind = (page-1)*page_size
        endind = (page)*page_size

        if startind < 0 or startind >= len(result_list) :
            abort(400)
        if not endind or endind < 0 :
            abort(400)

        if endind >= len(result_list) :
            endind = -1

        results_json = []
        for result in result_list[startind:endind] :
            results_json.append(marshal_result(result))

        return (results_json, (None if endind == -1 else page+1))


    def parginate(self, request) :
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
