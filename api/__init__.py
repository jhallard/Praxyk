#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, Response, g, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.bcrypt import Bcrypt
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, roles_required
from flask.ext.login import LoginManager, UserMixin, login_required

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property

import config


PRAXYK_API_APP = Flask(__name__) # our main flask app object
PRAXYK_API_APP.config.from_object('api.config') # our main flask app object configured from 'config.py'
PRAXYK_API_APP.config['SECURITY_TOKEN_AUTHENTICATION_KEY'] = 'token'
PRAXYK_API_APP.config['SECURITY_PASSWORD_HASH'] = "bcrypt"
PRAXYK_API_APP.config['SECURITY_PASSWORD_SALT'] = '__cryptonomicon__linux__'
PRAXYK_API_APP.config['WTF_CSRF_ENABLED'] = False

api = Api(PRAXYK_API_APP) # our flask.restful api object that we use for routing
db = SQLAlchemy(PRAXYK_API_APP) # this is our handle to the database
bcrypt = Bcrypt(PRAXYK_API_APP)  # used for password hashing

BASE_URL = "api.praxyk.com"
TRANSACTIONS_ROUTE= "/transactions/"
USERS_ROUTE = "/users/"
RESULTS_ROUTE = "/results/"

TRANSACTIONS_ENDPOINT = 'transactions'
TRANSACTION_ENDPOINT = 'transaction'
USER_ENDPOINT = 'user'
USERS_ENDPOINT = 'users'
RESULTS_ENDPOINT = 'results'


from models.sql.user import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(PRAXYK_API_APP, user_datastore)
PRAXYK_API_APP.config['SECURITY_CONFIRMABLE']
# Base = declarative_base() # base model for models to derive from

# from api import libs, models
