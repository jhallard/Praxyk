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
        super(PaymentHandlerRoute, self).__init__()

   #Only Stripe has access to this api route
    def post(self, webhook) :
        try :
            stripe_data = request.get_json()
            if webhook == "charge_failed":
                 user_payment_info = Payment_Info.query.filter_by(customer_id=stripe_data.data.object.customer).first()
                 user = user_payment_info.user
                 template = render_template('credit_card_charge_failed_email.html', user_name=user.name)
                 send_email(user.email, "PRAXYK: CREDIT CARD CHARGE FAILURE", template)
                 user.active = False
                 db.session.add(user)
                 db.session.commit()
                 return 200
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)

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
            
def charge_user(billing_data):
	pass



