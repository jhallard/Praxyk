#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /pod/bayes_spam/ route for the Praxyk API.

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

