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

# this map defines how a user db object get's transformed into a user api return object.
user_fields = {
    'name' : fields.String,
    'email' : fields.String,
    'user_id' : fields.String(attribute="id"),
    'uri' : fields.Url(USER_ENDPOINT, absolute=True),
    'transactions_url' : fields.String
}




# @info - class that users can post/get from , in order to active their account that they previously registered.
#         The specific id they post to (api.praxyk.com/confirm/{ID}) contains hashed inside of it the user's
#         email address that we sent the confirm code to. We use that email to register the user under.
class ConfirmRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        super(ConfirmRoute, self).__init__()

    def post(self, id) :
        args = self.reqparse.parse_args()
        email = self.confirm_token(id)
        if not email :
            return abort(404)	
        
        user = User.query.filter_by(email=email).first()
        user.active=True

        db.session.commit()
        return redirect("http://www.praxyk.com/login.html", code=302)

    # @marshal_with(user_fields, envelope='user')
    def get(self, id) :
        return self.post(id)
    
    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(PRAXYK_API_APP.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt=PRAXYK_API_APP.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        except:
            return False
        return email




