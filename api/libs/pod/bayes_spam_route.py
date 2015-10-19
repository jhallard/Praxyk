#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /users/ route for the Praxyk API.
##         This involved creating a class with the PUT, GET, POST, and 
##         DELETE methods defined. Once defined, the main API handler 
##         (../api_server.py) can simply import this class and use it to 
##         handle any user-related requests.

import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify, request, Response, g, abort, make_response, render_template, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with

from api import db, USER_ENDPOINT, USERS_ENDPOINT, CONFIRM_ENDPOINT, POD_BAYES_SPAM_ENDPOINT
from api import User, Role, user_datastore, mail

from libs.auth_route import *
from libs.transactions_route import *

class POD_Bayes_Spam_Route(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(POD_Bayes_Spam_Route, self).__init__()

