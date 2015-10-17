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
from api import db
from transaction import *

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    pwhash = db.Column(db.String(128))
    transactions = db.relationship('Transaction', backref='Creator', lazy='dynamic')

    @hybrid_property
    def transactions_url(self) :
       return "/transactions/%s/" % (self.id)

    def __init__(self, name, email, password) :
        self.name = name
        self.email = email
        self.pwhash = self.hashpw(password)

    def __repr__(self):
        return '<ID %r, Email %r>' % (self.id, self.email)

    def hashpw(self, password) :
        salt = str(self.id) + str(self.email) + str(self.id/2)
        return hashlib.sha512(salt + passwordw).hexdigest()
