#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines the users model and any models that are directly related
##         to the users of Praxyk services.

## Note - This model definition is shared across multiple servers and code branches, DO NOT
##        change this file unless you have permission or know exactly what you're doing. 

import __init__

from api import db, bcrypt, BASE_URL, TRANSACTIONS_ROUTE, USERS_ROUTE, RESULTS_ROUTE
from api import USERS_ENDPOINT, USER_ENDPOINT, TRANSACTIONS_ENDPOINT
from api import PRAXYK_API_APP, TOKEN_EXPIRATION

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask import url_for

from datetime import timedelta
from datetime import datetime as dt
import base64, M2Crypto

class Token(db.Model):
    __tablename__ = 'Tokens'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer(), db.ForeignKey('Users.id'))
    value      = db.Column(db.String(255), index=True, unique=True)
    created_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

    @hybrid_property
    def valid(self) :
        return dt.now() < self.expires_at()

    def __init__(self, user_id) :
        self.user_id = user_id
        self.value = base64.b64encode(M2Crypto.m2.rand_bytes(128)).replace("+", "a")
        self.created_at = dt.now()
        self.expires_at = self.created_at + timedelta(minutes=TOKEN_EXPIRATION)

    def __repr__(self):
        return '<User-ID %r, Value %r>' % (self.user_id, self.value)

