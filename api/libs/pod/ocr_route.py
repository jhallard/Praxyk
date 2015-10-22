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
from pprint import *

from flask import Flask, jsonify, request, Response, g, abort, make_response, render_template, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with

from api import db, USER_ENDPOINT, USERS_ENDPOINT, CONFIRM_ENDPOINT, POD_ENDPOINT, POD_OCR_ENDPOINT, RESULTS_ENDPOINT
from api import User, Role, user_datastore, mail, redis_pool, redis

from libs.auth_route import *
from libs.transactions_route import *
from models.nosql.result_base import *
from models.nosql.pod.result_pod_ocr import *

from queue import *

from werkzeug import secure_filename

# @info - route that allows user to enact request for the POD-OCR service.
#         users can post images to this route, we will process those images using
#         an OCR algorithm and return a string of whatever text we think is in the image
#         back to the user.
class POD_OCR_Route(Resource) :

    # convert datetime object to string formatted time
    def convert_timestr(self, dt) :                                                                                                                        
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(POD_OCR_Route, self).__init__()

    ALLOWED_EXTENSIONS = set(['bmp', 'tif', 'tiff', 'pdf', 'png', 'jpg', 'jpeg'])

    # @info - post route for pod-ocr service. Users must include their auth token and list of image files
    #         of the types shown above under the names 'files'. Files will all be grouped under a single 
    #         transaction with a single transaction ID. This ID can be used to get the results from the 
    #         /results/{trans_id} route
    @requires_auth
    def post(self) :
        try :
            caller = g._caller
            if not caller :
                abort(404)

            (new_trans, files_success) = self.setup_transaction(request, caller)

            caller.transactions.append(new_trans)
            db.session.commit()

            results = Results(transaction_id=new_trans.id, user_id=new_trans.user_id, size_total_KB=new_trans.size_total_KB)
            results.save()

            queue = task_lib.TaskQueue(redis_pool)
            jobs = self.enqueue_transaction(queue, new_trans, files_success, results)

            return jsonify({"code" : 200, "transaction" : marshal(new_trans, transaction_fields)})

        except Exception, e:
            sys.stderr.write("\nException (POD_OCR_Route:POST) : " + str(e))
            abort(404)

    # @info - take a newly made transaction db object and the list of files that that transaction
    #         deals with and enqueue them in the praxyk RQ task-queue to be processed.
    def enqueue_transaction(self, queue, new_trans, files_success, results) :
        file_count = 1
        jobs = []
        
        try :
            new_trans.status = Transaction.TRANSACTION_ACTIVE
            db.session.commit()
            for file_struct in files_success :
                trans = {
                     "trans_id"    : new_trans.id,
                     "file_num"    : file_count,
                     "files_total" : new_trans.uploads_total,
                     "created_at"  : new_trans.created_at,
                     "finished_at" : new_trans.finished_at,
                     "status"      : new_trans.status,
                     "user_id"     : new_trans.user_id
                }
                result = Result_POD_OCR(created_at = datetime.datetime.now(),
                                        transaction_id = new_trans.id,
                                        item_number = file_count,
                                        item_name = file_struct['name'],
                                        status = ResultBase.RESULT_ACTIVE,
                                        size_KB = file_struct['size'])
                result.save()
                # results.results.append(result)
                jobs.append(queue.enqueue_pod(trans, file_struct))
                file_count += 1
            res = Result_POD_OCR.query.filter(transaction_id=results.transaction_id).execute()
            results.save()
            return jobs
        except Exception, e:
            sys.stderr.write("\nException (POD_OCR_route:enqueue_trans) : " + str(e))
            return []
    
    # @info - takes the raw request from the user (containing the images to be processed) and the
    #         id of the caller, turns these items into a transaction object that can be stored in 
    #         the SQL db. See /models/sql/transaction.py for more info on the transaction model.
    def setup_transaction(self, request, caller) :
        try :
            (files_success, files_failed) = self.get_files_from_request(request)

            command_url = url_for(POD_OCR_ENDPOINT)

            new_trans = Transaction(user_id=caller.id, command_url=command_url, status=Transaction.TRANSACTION_NEW)

            new_trans.uploads_success =  0 if not files_success else len(files_success)
            new_trans.uploads_failed =   0 if not files_failed else len(files_failed)
            new_trans.uploads_total  = new_trans.uploads_success + new_trans.uploads_failed

            size_total_KB = 0.0
            for x in files_success :
                size_total_KB += x['size']
            new_trans.size_total_KB = size_total_KB

            if not new_trans.uploads_success or new_trans.uploads_success == 0 :
                new_trans.status = Transaction.TRANSACTION_FAILED

            return (new_trans, files_success)
        except Exception, e:
            sys.stderr.write("\nException (POD_OCR_route:setup_trans) : " + str(e))
            return ([], []) 


    # @info - takes the raw request dict and gathers the files from it, parses them into success/failure
    #         based on if the images were able to upload correctly and/or are the correct file type, and 
    #         returns these to the caller.
    def get_files_from_request(self, request) :
        try :
            files = []
            if request.files :
                files = request.files.getlist('files')
            if not files :
                files = request.values.get('files', [])
            if not files :
                return ([], [])

            files_success = [] 
            files_failed  = []

            for ufile in files:
                if ufile and self.allowed_file(ufile.filename):
                    data = ufile.read()
                    ufile.seek(0, os.SEEK_END)
                    file_length_bytes = ufile.tell()
                    file_length = file_length_bytes/1000.0
                    filename = secure_filename(ufile.filename)
                    files_success.append({"name" : filename, "data" : data, "size" : file_length})
                elif ufile : # if it's not an allowed file mark it so we can tell the user such
                    files_failed.append(ufile.filename)
                else : # else just put an anon failure in the list so we still know a file upload failed
                    files_failed.append("N/A")

            return (files_success, files_failed)
        except Exception, e:
            sys.stderr.write("\nException (POD_OCR_route:get_files_from_req) : " + str(e))
            return ([], []) 


    # For a given file, return whether it's an allowed type or not
    def allowed_file(self, filename):
        return True or '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
