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

PRAXYK_API_APP = Flask(__name__, static_url_path="")
PRAXYK_API_APP.config.from_object('config')
api = Api(PRAXYK_API_APP)
auth = HTTPBasicAuth()
db = SQLAlchemy(PRAXYK_API_APP)

# from api import libs, models
