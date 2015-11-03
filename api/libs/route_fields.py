#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - this file contains all the marshal'ing fields that turn database objects into 
##         dictionaries that can jsonified and returned to the user

from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
from api import *

def convert_timestr(dt) :
    if not dt :
        return '0-0-0 00:00:00'
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# @info - have to make our own function for marshal Result objects from the redis db
def marshal_result(res) :
    return { "item_number"   : res.item_number,
             "item_name"     : res.item_name,
             "status"        : res.status,
             "size_KB"       : res.size_KB,
             "finished_at"   : convert_timestr(res.finished_at),
             "created_at"    : convert_timestr(res.created_at),
             "uri"           : url_for(RESULT_ENDPOINT, id=res.transaction_id, page_size=1, page=res.item_number, _external=True),
             "prediction"    : { "result_string" : res.result_string }
    }


# this map defines how a user db object get's transformed into a user api return object.
user_fields = {
    'name'            : fields.String,
    'email'           : fields.String,
    'user_id'         : fields.String(attribute="id"),
    'uri'             : fields.Url(USER_ENDPOINT, absolute=True),
    'active'          : fields.Boolean,
    'transactions_url': fields.String,
    'created_at'      : fields.DateTime(dt_format='iso8601')
}


transaction_fields = {
    'trans_id'        : fields.String(attribute="id"),
    'name'            : fields.String,
    'user_id'         : fields.Integer,
    'command_url'     : fields.String,
    'data_url'        : fields.String,
    'results_url'     : fields.String,
    'user_url'        : fields.String,
    'service'         : fields.String,
    'model'           : fields.String,
    'version'         : fields.String,
    'status'          : fields.String,
    'uploads_total'   : fields.Integer,
    'uploads_success' : fields.Integer,
    'uploads_failed'  : fields.Integer,
    'size_total_KB'   : fields.Float,
    'created_at'      : fields.DateTime(dt_format='iso8601'), #'rfc822'),
    'finished_at'     : fields.DateTime(dt_format='iso8601'), #'rfc822'),
    'uri'             : fields.Url(TRANSACTION_ENDPOINT, absolute=True)
}

transactions_fields = {
    'transactions' : fields.Nested(transaction_fields),
    'user_id'      : fields.Integer
}
