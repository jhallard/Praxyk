#!/usr/bin/env python

## @auth John Allard, Ryan Coley, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /payment_handler/ route for the praxyk api. Stripe posts api
## calls to this to deal with payment events


from flask import Flask, jsonify, request, Response, g, abort, make_response, redirect
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
from flask.ext.security import Security, SQLAlchemyUserDatastore

from itsdangerous import URLSafeTimedSerializer

from api import db, CONFIRM_ENDPOINT, USER_ENDPOINT
from api import User, Role, user_datastore

from auth_route import *

from libs.route_fields import *


# @info - class that users can post/get from , in order to active their account that they previously registered.
#         The specific id they post to (api.praxyk.com/confirm/{ID}) contains hashed inside of it the user's
#         email address that we sent the confirm code to. We use that email tore gister the user under.
class PaymentHandlerRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        super(ConfirmRoute, self).__init__()
   #Only Stripe has access to this api route
    def post(self, id) :
        try :
            args = self.reqparse.parse_args()
            email = self.confirm_token(id)
            if not email :
                return abort(404)	
            
            user = User.query.filter_by(email=email).first()
            user.active=True

            db.session.commit()
            return redirect("http://www.praxyk.com/login.html", code=302)
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)




