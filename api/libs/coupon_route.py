#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /confirm/ route for the praxyk api. Keys that contain
##         the user's email are generated and email to each use upon registration. When they read 
##         those emails and click the links provided, it will bring them to a page here where they 
##         can submit their full account information for registration,


import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify, request, Response, g, abort, make_response, redirect, render_template, url_for
from flask.ext.restful import Api, Resource, reqparse, fields
from flask.ext.security import Security, SQLAlchemyUserDatastore

from api import db, PAYMENT_ENDPOINT,USER_ENDPOINT,USERS_ENDPOINT,COUPON_ENDPOINT
from api import User, Role, user_datastore

from auth_route import *
from libs.route_fields import *

import stripe
from api.config import stripe_secret_key
stripe.api_key = stripe_secret_key


# @info - class that users can post/get from , in order to active their account that they previously registered.
#         The specific id they post to (api.praxyk.com/confirm/{ID}) contains hashed inside of it the user's
#         email address that we sent the confirm code to. We use that email tore gister the user under.
class CouponRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(CouponRoute, self).__init__()

    @requires_auth
    def post(self, id) :
        self.reqparse.add_argument('coupon', type=str, required=True, location='json')
        args = self.reqparse.parse_args()
        caller = g._caller
        if not caller or not validate_owner(caller, id) :
            abort(404)
	user = User.query.get(id)
        try :
            customer = stripe.Customer.retrieve(user.payment_info.customer_id)
            customer.coupon = args.coupon
            result = customer.save()
            print(result)

            return jsonify({'code':200,'message':'The coupon was successfully added to your account!'})
        except stripe.error.InvalidRequestError, e:
            return jsonify({'code':200,'message':'There was an error trying to add your coupon! Please make sure that coupon is valid!'})
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)




