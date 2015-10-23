#!/usr/bin/env python

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the authorization functionality needed
##         by this API. That includes wrappers to guarentee user authentication 
##         via auth-tokens, and owner-resource validation to ensure that regular
##         users can only access their own resources but admins can access anyones


import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify, request, Response, g, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with

from flask.ext.security import (Security, SQLAlchemyUserDatastore, login_required, current_user,
                                roles_required, auth_token_required, UserMixin, RoleMixin)

from functools import wraps

from api import db, PRAXYK_API_APP
from api import User, Token, Role 

from libs.route_fields import user_fields



# @info - decorator function, any function that this decorator is applied to will
#         have to have it's token argument validated with the auth util. All this
#         does is make sure the given token exists in the database and isn't expired.
def requires_auth(f):
    @wraps(f)                                                                                                                                        
    def decorated(*args, **kwargs):
        try :
            token = request.values.get('token')
            if not token:
                token = request.json.get('token')
            if not token:
                abort(403)
    	    token = Token.query.filter_by(value="%s"%token).first_or_404()
            user = None if not token else token.user
            if not token or not user :
                return abort(403, "Token Could not Be Authenticated")
	        if not token.valid :
		        return abort(403, "Token has Expired")
            g._caller = user
            return f(*args, **kwargs)
        except Exception, e:
            print str(e)
            return abort(403)
    return decorated

# @info - called to make sure that the owner of a resource is the one trying to access
#         it, also allows root and admin users to access resource.
def validate_owner(caller, owner_id) :
    try :
        if caller and caller.id == owner_id :
            return True
        roles = caller.roles
        if not roles :
            return False
        for role in roles :
            if role == Role.ROLE_ROOT or role == Role.ROLE_ADMIN :
                return True
        return False
    except Exception, e :
        return False


# @info - this route can be used to post credentials and recieve a token in response.
#         The /login/ /auth/ and other routes point here
class AuthRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, location='json')
        self.reqparse.add_argument('password', type=str, required=True, location='json')
        super(AuthRoute, self).__init__()

    def post(self) :
        try : 
            args = self.reqparse.parse_args()
            user = User.authenticate(args['email'], args['password'])

            if not user :
                abort(404)

            # first try and get an existing and valid token
            tokens = Token.query.filter((Token.user_id==user.id and Token.valid)).first()
            if tokens :
                return jsonify({"code" : 200, "user" : marshal(user, user_fields), "token" : tokens.value})
                
            # otherwise make them a new one
            new_token = Token(user_id=user.id)
            if not new_token :
                abort(403)
            user.tokens.append(new_token)

            db.session.add(user)
            db.session.commit()
            return jsonify({"code" : 200, "user" : marshal(user, user_fields), "token" : new_token.value})
        except Exception, e :
            print str(e)
            return abort(403)

    @requires_auth
    def delete(self, id) :
        pass
    




