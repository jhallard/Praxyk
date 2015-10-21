#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## Note - This model definition is shared across multiple servers and code branches, DO NOT
##        change this file unless you have permission or know exactly what you're doing. 

import __init__

from api import db, BASE_URL, TRANSACTIONS_ROUTE, USERS_ROUTE, RESULTS_ROUTE
from api import USERS_ENDPOINT, USER_ENDPOINT, TRANSACTIONS_ENDPOINT, RESULTS_ENDPOINT
from api import TRANSACTION_NEW, TRANSACTION_FINISHED, TRANSACTION_ACTIVE

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask import url_for

import datetime

## @info - this class defines the results-table for the POD-OCR service. It derives from the abstract
##         ResultBase base class and adds in only the columns needed to store the result data specific
##         to the OCR routine.
# class POD_OCR_Result(db.Model, ResultBase) :
    # __tablename__ = "POD_OCR_Results"
# 
    # id              = db.Column(db.Integer, primary_key = True)
    # created_at      = db.Column(db.DateTime)
    # finished_at     = db.Column(db.DateTime)
    # item_number     = db.Column(db.Integer, index=True, nullable=False)
    # item_name       = db.Column(db.String(200), index=True, nullable=False)
    # status          = db.Column(db.String(100), index=True) # something like 'new', 'active', 'orphaned', etc.
    # size_KB         = db.Column(db.Float)   # the total size of uploaded data in KB
# 
    # return_string  = db.Column(db.Text)
# 
    # @declared_attr
    # def transaction_id(self)  :
        # return db.Column(db.Integer, db.ForeignKey('Transactions.id'))
# 
    # @declared_attr
    # def user_id(self) : 
        # return db.Column(db.Integer, db.ForeignKey('Users.id'))
# 
    # @hybrid_property
    # def transaction_url(self) :
       # return url_for(TRANSACTION_ENDPOINT, id=self.transction_id, _external=True) 
# 
    # @hybrid_property
    # def user_url(self) :
       # return url_for(USER_ENDPOINT, id=self.user_id, _external=True) 
# 
    # def __init__(self, user_id, status, item_name, size_KB, item_number, created_at=None, finished_at=None) :
        # self.created_at      = created_at
        # self.finished_at     = finished_at
        # self.user_id         = user_id
        # self.status          = status
        # self.size_KB         = size_total_KB
        # self.item_name       = item_name
        # self.item_number     = item_number
# 
 # 
    # def __repr__(self):
        # rep = '<ResultID %r, TransactionID %r, UserID %s, Status %s, ItemNum %r, CreatedAt %s>'
        # return rep % (self.id, self.transaction_id, self.user_id, self.status, self.item_number, str(self.created_at) )
# 
# 
    # def __init__(self, **kwargs) : 
        # super(POD_OCR_Result, self).__init__(return_string, **kwargs)
        # self.return_string = return_string
 # 
    # def __repr__(self):
        # rep = '<ResultID %r, TransactionID %r, UserID %s, Status %s, ItemNum %r, CreatedAt %s>'
        # return rep % (self.id, self.transaction_id, self.user_id, self.status, self.item_number, str(self.created_at) )
