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


class Transaction(db.model) :
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    command_url = db.Column(db.String(500))
    data_url = db.Column(db.String(500)) # url to access the input data associated with transaction

    def __repr__(self):
        return '<Transaction %r>' % (self.id)
