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
from flask.ext.mail import Message
from flask_mail import Mail

from flask.ext.security import Security, SQLAlchemyUserDatastore

from itsdangerous import URLSafeTimedSerializer

from api import db, USER_ENDPOINT, USERS_ENDPOINT, CONFIRM_ENDPOINT
from api import User, Role, user_datastore, mail

from auth_route import *

# this map defines how a user db object get's transformed into a user api return object.
user_fields = {
    'name' : fields.String,
    'email' : fields.String,
    'user_id' : fields.String(attribute="id"),
    'uri' : fields.Url(USER_ENDPOINT, absolute=True),
    'transactions_url' : fields.String
}

# @info - class with routes that contain a user id 
# ie `GET api.praxyk.com/users/12345`
class UserRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=False, location='json')
        self.reqparse.add_argument('password', type=str, required=False, location='json')
        self.reqparse.add_argument('name', type=str, required=False, location='json')
        super(UserRoute, self).__init__()

    @marshal_with(user_fields, envelope='user')
    @requires_auth
    def get(self, id) :
        try :
            caller = g._caller
            if not caller or not validate_owner(caller, id) :
                abort(404)
            user =  User.query.get(id)
            if not user :
                abort(404)
            return user
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)



    @marshal_with(user_fields, envelope='user')
    @requires_auth
    def put(self, id) :
        try :
            caller = g._caller
            if not caller or not validate_owner(caller, id) :
                abort(404)

            args = self.reqparse.parse_args()
            user = User.query.get(id)

            if not user :
                abort(404)

            if args.get('email', None) :
                user.email = args['email']

            if args('password', None) :
                user.password = args['password'] # hashed automatically upon set

            db.session.add(user)
            db.session.commit()
            return user
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

    @marshal_with(user_fields, envelope='user')
    @requires_auth
    def delete(self, id) :
        caller = g._caller
        if not caller or not validate_owner(caller, id) :
            abort(404)
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return user



# @info - class with routes that don't contain a user id 
# ie `POST api.praxyk.com/users/`
class UsersRoute(Resource) :

    def __init__(self) :
        self.transaction_id = None
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, location='json')
        self.reqparse.add_argument('name', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        super(UsersRoute, self).__init__()

    @marshal_with(user_fields, envelope='user')
    def post(self) :
        try : 
            subject = "Confirm Your Praxyk Machine-Learning Services Account"
            args = self.reqparse.parse_args()
            email=args.email

            # if user exists already return error
            if User.query.filter_by(email=email).first() :
                abort(400)

            new_user = user_datastore.create_user(name=args.name, email=args.email, password=args.password, active=False)
            role = user_datastore.find_role(Role.ROLE_USER)
            user_datastore.add_role_to_user(new_user, role)
            db.session.commit()

            token = self.generate_confirmation_token(email)
            confirm_url = confirm_url=url_for(CONFIRM_ENDPOINT, id=token, _external=True)
            template = render_template('confirm_email.html', confirm_url=confirm_url, user_name=args.name)
            if not self.send_email(email, subject, template) :
                db.session.delete(new_user)
                abort(404)

            return new_user
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

    def generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(PRAXYK_API_APP.config['SECRET_KEY'])
        return serializer.dumps(email, salt=PRAXYK_API_APP.config['SECURITY_PASSWORD_SALT'])
	
    def send_email(self, to, subject, template):
        try :
            msg = Message(
                subject,
                recipients=[to],
                html=template,
                sender=PRAXYK_API_APP.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            return True
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            return False
    




