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
from api import USERS_ENDPOINT, USER_ENDPOINT, TRANSACTIONS_ENDPOINT

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask import url_for


class Transaction(db.Model) :
    __tablename__ = "Transactions"

    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    command_url = db.Column(db.String(500))
    data_url = db.Column(db.String(500)) # url to access the input data associated with transaction
    status = db.Column(db.String(100)) # something like 'new', 'active', 'orphaned', etc.

    @hybrid_property
    def results_url(self) :
       return url_for(RESULTS_ENDPOINT, id=self.id, _external=True) 

    def __init__(self, user_id, status="new") :
        self.created_at = datetime.datetime.now()
        self.user_id = user_id
        self.status = status

 
    def __repr__(self):
        return '<Transaction %r>' % (self.id)
