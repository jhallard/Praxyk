#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Ryan Coley, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines the users model and any models that are directly related
##         to the users of Praxyk services.

## Note - This model definition is shared across multiple servers and code branches, DO NOT
##        change this file unless you have permission or know exactly what you're doing. 

import __init__

from api import db, bcrypt, BASE_URL, TRANSACTIONS_ROUTE, USERS_ROUTE, RESULTS_ROUTE
from api import USERS_ENDPOINT, USER_ENDPOINT, TRANSACTIONS_ENDPOINT
from api import PRAXYK_API_APP

# flask stuff (networking and security)
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property 
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask.ext.security.utils import encrypt_password, verify_password
from flask import url_for
from datetime import datetime as dt

#stripe api
import stripe
from api.config import stripe_secret_key
stripe.api_key = stripe_secret_key

# grab other models we depend on
from token import *
from transaction import *
from role import *
from user import *

class Payment_Info(db.Model, UserMixin):
	__tablename__ = "Payment_Info"
	id             = db.Column(db.Integer, primary_key=True)
	user_id        = db.Column(db.Integer, db.ForeignKey('Users.id'))
	customer_id    = db.Column(db.String(32), unique=True)
	card_id        = db.Column(db.String(32), unique=True)

	def __init__(self, email) :
           self.customer_id = create_customer(email=email)
           self.card_id = None

def create_customer(email):
    result_json = stripe.Customer.create(email=email,plan="POD_Services")
    return result_json.id 
