#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /confirm/ route for the praxyk api. Keys that contain
##         the user's email are generated and email to each use upon registration. When they read 
##         those emails and click the links provided, it will bring them to a page here where they 
##         can submit their full account information for registration,


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
class ConfirmRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        super(ConfirmRoute, self).__init__()

    def post(self, id) :
        try :
            args = self.reqparse.parse_args()
            email = self.confirm_token(id)
            if not email :
                return abort(404)	
            
            user = User.query.filter_by(email=email).first()
            user.confirmed=True

            db.session.commit()
            return redirect("http://www.praxyk.com/login.html", code=302)
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

    def get(self, id) :
        return self.post(id)
    
    def confirm_token(self, token, expiration=3600):
        try :
            serializer = URLSafeTimedSerializer(PRAXYK_API_APP.config['SECRET_KEY'])
            try:
                email = serializer.loads(token, salt=PRAXYK_API_APP.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
            except:
                return False
            return email
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            return None




