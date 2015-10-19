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
from api import User, Role, user_datastore, mail, redis
from api import TRANSACTION_NEW, TRANSACTION_FINISHED, TRANSACTION_FAILED, TRANSACTION_ACTIVE

from libs.auth_route import *
from libs.transactions_route import *

from werkzeug import secure_filename

# @info - class with routes that contain a user id 
# ie `GET api.praxyk.com/users/12345`
class POD_OCR_Route(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(POD_OCR_Route, self).__init__()

    ALLOWED_EXTENSIONS = set(['bmp', 'tif', 'tiff', 'pdf', 'png', 'jpg', 'jpeg'])

    @marshal_with(transaction_fields, envelope='transaction')
    @requires_auth
    def post(self) :
        try :
            caller = g._caller
            if not caller :
                abort(404)

            (files_success, files_failed) = self.get_files_from_request(request)

            command_url = url_for(POD_OCR_ENDPOINT)

            new_trans = Transaction(user_id=caller.id, command_url=command_url, status=TRANSACTION_NEW)

            new_trans.uploads_success =  0 if not files_success else len(files_success)
            new_trans.uploads_failed =   0 if not files_failed else len(files_failed)
            new_trans.uploads_total  = new_trans.uploads_success + new_trans.uploads_failed

            size_total_KB = 0.0
            for x in files_success :
                size_total_KB += x['size']
            new_trans.size_total_KB = size_total_KB

            if not new_trans.uploads_success or new_trans.uploads_success == 0 :
                new_trans.status = TRANSACTION_FAILED

            caller.transactions.append(new_trans)
            db.session.commit()

            return new_trans
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

    def get_files_from_request(self, request) :
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
            print ufile.filename + "\n\n"
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



    # For a given file, return whether it's an allowed type or not
    def allowed_file(self, filename):
        return True or '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
