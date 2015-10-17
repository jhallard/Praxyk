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

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask import url_for



roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('Users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('Roles.id')))


class Role(db.Model, RoleMixin):
    __tablename__ = "Roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(500))

    names = ["user", "test", "admin"]
    def __init__(self, name="user", description=None) :
        if name not in name :
            self.name = "user"
        else :
            self.name = name
        self.description = description

class User(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    transactions = db.relationship('Transaction', backref='Creator', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    @hybrid_property
    def transactions_url(self) :
       return url_for(TRANSACTIONS_ENDPOINT, user_id=self.id, _external=True) 

    def __init__(self, name, email, password, active, roles) :
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.roles = roles

    def is_authenticated(self) :
        return True

    def __repr__(self):
        return '<ID %r, Email %r>' % (self.id, self.email)

    def verifypw(self, plaintext) :
        return bcrypt.check_password_hash(self._password, plaintext)

    def authenticate(email, plaintext) :
        user = User.query.filter_by(email=email).first()
        if user and user.verifypw(plaintext) :
            return user
        return None

    def identity(payload) :
        user_id = payload['identity']
        return User.query.get(user_id, None)
