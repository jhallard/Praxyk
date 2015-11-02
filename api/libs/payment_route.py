#!/usr/bin/env python

## @auth John Allard, Ryan Coley, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

## @info - This file defines all of the /payment/ route for the praxyk api. The user
## is able to add, remove, update and delete their payment information.


from flask import Flask, jsonify, request, Response, g, abort, make_response, redirect
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
from flask.ext.security import Security, SQLAlchemyUserDatastore

from itsdangerous import URLSafeTimedSerializer

from api import db, USER_ENDPOINT,USERS_ENDPOINT
from api import User, Role, user_datastore

from auth_route import *
from libs.route_fields import *


# @info - class that users can post/get from , in order to active their account that they previously registered.
#         The specific id they post to (api.praxyk.com/confirm/{ID}) contains hashed inside of it the user's
#         email address that we sent the confirm code to. We use that email tore gister the user under.
class PaymentRoute(Resource) :

    def __init__(self) :
        self.reqparse = reqparse.RequestParser()
        super(PaymentRoute, self).__init__()
        
   #Add Payment info only if none on file
    @requires_auth
    def post(self, id) :
        try :
            user = User.query.get(id)
        
            if not user.card_id == None :
               return jsonify({'code':400,'message':"There is already a card on file! Please delete that card to add another."})
               
            self.reqparse.add_argument('name', type=str, required=True, location='json')
            self.reqparse.add_argument('address1', type=str, required=True, location='json')
            self.reqparse.add_argument('address2', type=str, required=True, location='json')
            self.reqparse.add_argument('city', type=str, required=True, location='json')
            self.reqparse.add_argument('state', type=str, required=True, location='json')
            self.reqparse.add_argument('zip', type=int, required=True, location='json')
            self.reqparse.add_argument('credit_number', type=int, required=True, location='json')
            self.reqparse.add_argument('exp_month', type=int, required=True, location='json')
            self.reqparse.add_argument('exp_year', type=int, required=True, location='json')
            self.reqparse.add_argument('cvc', type=str, required=True, location='json')
            args = self.reqparse.parse_args()
            
            token = stripe.Token.create(
               card={
                  "number":args.credit_number,
                  "exp_month":args.exp_month,
                  "exp_year":args.exp_year,
                  "cvc":args.cvc,
                  "name":args.name,
                  "address_city":args.city,
                  "address_line1":args.address1,
                  "address_line2":args.address2,
                  "address_state":args.state,
                  "address_zip":args.zip
                  
               })
               
            customer = stripe.Customer.retrieve(user.customer_id)
            card = customer.sources.create(source=token.id)
               
            user.card_id = card.id
               
            db.session.add(user)
            db.session.commit()
               
            return jsonify({'code':200,'message':'Your card was successfully added!'})
            
        except stripe.error.CardError, e:            
            return jsonify({'code': 400,'message':'There was an error with your card! Please make sure that all details are correct.'})
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)
            
   #Retrieve Payment Info
    @requires_auth
    def get(self, id) :
	user = User.query.get(id)
	if user.card_id == None:
		return jsonify({'code':200,'message':'Your card was successfully removed!'})
	try:
            
         customer = stripe.Customer.retrieve(user.customer_id)
         card = customer.sources.retrieve(user.card_id).delete()
        
         return card
        
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)
        
    #Remove Payment Info
    @requires_auth
    def delete(self,id):
        user = User.query.get(id)
        try:
         if user.card_id == None:
            return jsonify({'code':400,'message':"There is not a card on file!"})
            
         customer = stripe.Customer.retrieve(user.customer_id)
         card = customer.sources.retrieve(user.card_id).delete()
         
         if not card.deleted :
            return jsonify({'code':400,'message':"There was a problem removing you card!"})
            
         user.card_id = None
         
         db.session.add(user)
         db.session.commit()
        
         return jsonify({'code':200,'message':'Your card was successfully removed!'})
        
        except Exception, e:
            sys.stderr.write("Exception : " + str(e))
            abort(404)




