#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, Response, g, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property

import config

PRAXYK_API_APP = Flask(__name__)
PRAXYK_API_APP.config.from_object('config')
api = Api(PRAXYK_API_APP)
auth = HTTPBasicAuth()
db = SQLAlchemy(PRAXYK_API_APP)

BASE_URL = "api.praxyk.com"
TRANSACTIONS_ROUTE= "/transactions/"
USERS_ROUTE = "/users/"
RESULTS_ROUTE = "/results/"


# Base = declarative_base() # base model for models to derive from

# from api import libs, models
