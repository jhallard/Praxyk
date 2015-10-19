#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines the transaction model and any models that are directly related
##         to the transactions that are created as a result of user interaction with praxyk
##         services.

## Note - This model definition is shared across multiple servers and code branches, DO NOT
##        change this file unless you have permission or know exactly what you're doing. 

import __init__

from api import db, BASE_URL, TRANSACTIONS_ROUTE, USERS_ROUTE, RESULTS_ROUTE
from api import USERS_ENDPOINT, USER_ENDPOINT, TRANSACTIONS_ENDPOINT, RESULTS_ENDPOINT
from api import TRANSACTION_NEW, TRANSACTION_FINISHED, TRANSACTION_ACTIVE

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask import url_for

import datetime


class Transaction(db.Model) :
    __tablename__ = "Transactions"

    id              = db.Column(db.Integer, primary_key = True)
    created_at      = db.Column(db.DateTime)
    finished_at     = db.Column(db.DateTime)
    user_id         = db.Column(db.Integer, db.ForeignKey('Users.id'))
    command_url     = db.Column(db.String(500))
    status          = db.Column(db.String(100)) # something like 'new', 'active', 'orphaned', etc.
    uploads_total   = db.Column(db.Integer) # total num items they tried to upload for this trans
    uploads_success = db.Column(db.Integer) # number of uploads that worked
    uploads_failed  = db.Column(db.Integer) # number that failed (total - success)
    size_total_KB   = db.Column(db.Float)   # the total size of uploaded data in KB

    @hybrid_property
    def results_url(self) :
       return url_for(RESULTS_ENDPOINT, id=self.id, _external=True) 

    @hybrid_property
    def data_url(self) :
        return "N/A"
        # @TODO - When we implement a seperate data-handling server put the url here for this transactions data
        # return url_for(RESULTS_ENDPOINT, id=self.id, _external=True) 

    @hybrid_property
    def user_url(self) :
       return url_for(USER_ENDPOINT, id=self.user_id, _external=True) 

    def __init__(self, user_id, command_url, status=TRANSACTION_NEW, size_total_KB = 0,
                 uploads_total=0, uploads_success=0, uploads_failed=0) :
        self.created_at      = datetime.datetime.now()
        self.user_id         = user_id
        self.status          = status
        self.command_url     = command_url
        self.size_total_KB   = size_total_KB
        self.uploads_total   = uploads_total
        self.uploads_success = uploads_success
        self.uploads_failed  = uploads_failed

 
    def __repr__(self):
        rep = '<TransactionID %r, UserID %s, CommandURL %s, Status %s, NumItems %r, CreatedAt %s>'
        return rep % (self.id, self.user_id, self.command_url, self.status, self.uploads_success, str(self.created_at) )
