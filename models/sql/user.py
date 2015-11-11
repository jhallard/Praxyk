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
from api import PRAXYK_API_APP

# flask stuff (networking and security)
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask.ext.security.utils import encrypt_password, verify_password
from flask import url_for
from datetime import datetime as dt

# grab other models we depend on
from token import *
from transaction import *
from role import *
from payment_info import *


class User(db.Model, UserMixin):
    __tablename__ = 'Users'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), index=True)
    email        = db.Column(db.String(120), index=True, unique=True)
    _password    = db.Column(db.String(255))
    active       = db.Column(db.Boolean())
    confirmed    = db.Column(db.Boolean())
    created_at   = db.Column(db.DateTime)
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    roles        = db.relationship('Role', secondary=roles_users, backref=db.backref('user', lazy='dynamic'))
    tokens       = db.relationship('Token', backref='user', lazy='dynamic')
    payment_info = db.relationship('Payment_Info', backref='user', lazy='dynamic')

    @hybrid_property
    def password(self) :
        return self._password

    @password.setter
    def set_password(self, plaintext) :
        self._password = encrypt_password(plaintext)

    @hybrid_property
    def transactions_url(self) :
       return url_for(TRANSACTIONS_ENDPOINT, user_id=self.id, _external=True) 

    def __init__(self, name, email, password, confirm=False, roles=None, active=False) :
        self.name = name
        self.email = email
        self.password = password
        self.created_at = dt.now()
        self.active = active
        self.confirmed = confirm
        self.roles = roles
        self.payment_info = [Payment_Info(email=email)]

    def __repr__(self):
        return '<ID %r, Email %r>' % (self.id, self.email)

    def verifypw(self, plaintext) :
        return verify_password(plaintext, self._password) #bcrypt.check_password_hash(self._password, plaintext)

    @staticmethod
    def authenticate(email, plaintext) :
        try :
            user = User.query.filter_by(email=email).first()
            if not user.confirmed :
                return None
            if user and user.verifypw(plaintext) :
                return user
        except Exception, e: 
            print str(e)
            return None
        return None
