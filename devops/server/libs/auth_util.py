#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT


import hashlib, uuid
import datetime
from datetime import timedelta
from os.path import expanduser

from db_util import *
from log_util import *


# @info - This class handles authentication of user requests for interaction with the instance-management code.
#         This class will check if a user exists, allow creations of new users, validate user login via username
#         and password and via token (the preferred method). 
class authUtil :

    # @info - Takes a dictionary of 3 required arguments. The first is an instance of the dbUtil class which is connected
    #         to the relevant devops database. The second is a logUtil object for us to log through, the third is a string,
    #         our client key that we log through.
    def __init__(self, args) :
        self.dbutil = args['dbutil']
        self.logger = args['logutil']
        self.logclient = args['logclient']
        self.ndbUsers = "Users"
        self.ndbTokens = "Tokens"

    def check_user_exists(self, name) :
        res = self.dbutil.query(self.ndbUsers, "*", "username='%s'"%name)
        return res is not None and len(res) > 0

    # @info - takes a dictionary of arguments containing 'username', 'pwhash' (512 bit), 'email' (optional).
    #         creates a new user if one with that name doesn't exist, if one exists already returns None.
    #         if the user is created successfully it tries to create an access token for the user, it that 
    #         fails it returns none, otherwise it returns the new access token.
    def create_user(self,userargs) :
        un = userargs['username']
        pwhash = userargs['pwhash']
        email = userargs.get('email', "")

        vals = [("username", un), ("pwhash", pwhash), ("email", email)]

        if self.check_user_exists(un) :
            self.logger.log_event(self.logclient, "CREATE USER", "f", ['Username', 'Email'], (un, email), "User Already Exists in DB")
            return None 

        if self.dbutil.insert(self.ndbUsers, vals) : 
            self.logger.log_event(self.logclient, "CREATE USER", 's', ['Username', 'Email'], (un, email))
        else :
            self.logger.log_event(self.logclient, "CREATE USER", 'f', ['Username', 'Email'], (un, email))
            return None

        return  self.make_new_token(un)
        

    # @info - ensures that a given token exists in the token database
    def validate_token(self, tok) :
        self.logger.log_event(self.logclient, "TOKEN VALIDATE", 'a')
        results = self.dbutil.query(self.ndbTokens, 'val', "val='%s'", "created_at ASC", limit=1)
        ret = (len(results) > 1)
        return self.logger.log_event(self.logclient, "TOKEN VALIDATE", 's' if ret else 'f')

    # @info - takes a username and a pwhash and validates that the credential are correct. 
    #         normally only used to get validate a user when their token expires and they
    #         need a new one.
    def validate_user(self, username, pwhash) :
        self.logger.log_event(self.logclient, "USER VALIDATE", 'a', ['User'], (username))
        user = self.dbutil.query(self.ndbUsers, '*', "username='%s'"%namename, limit=1)

        if user :
            user = user[0] # it's the first and only row returned.

        ret = (user[1] == pwhash)
        return self.logger.log_event(self.logclient, "USER VALIDATE", 's' if ret else 'f', ['User'], (username))

    # @info - takes a user and gets a valid token for them. If none are available it makes a new one and returns
    #         it. This is called after the validate_user function is called.
    def get_token(self, user) :
        if not self.check_user_exists(user) :
            return self.logger.log_event(self.logclient, "TOKEN FETCH", 'f', ['User'], (user), "User Doesn't Exist")

        tok = self.dbutil.query(self.ndbTokens, '*', "user='%s'"%user, order_by="created_at ASC", limit=1)

        if not tok :
            self.logger.log_event(self.logclient, "TOKEN FETCH", 'f', ['User'], (user), "No Tokens Found")
            return None
        else :
            expires_at = tok[0][3]
            if self.dt_to_str(expires_at) <  self.dt_to_str(datetime.datetime.now()) :
                return self.make_new_token(user)
            else :
                return tok[0][1] # the token value

    # @info - get a users attributes from the database base on the username
    def get_user(self, name) :
        if not self.check_user_exists(name) :
            return self.logger.log_event(self.logclient, "USER INFO FETCH", 'f', ['User'], (name), "User Doesn't Exist")
        user = self.dbutil.query(self.ndbUsers, '*', "username='%s'"%name, limit=1)

        if user :
            user = user[0] # it's the first and only row returned.

        return {'username' : user[0], 'pwhash' : user[1], 'email' : user[2]}



    # @info - make a new valid token for the user, put it in the database, and return the token
    #         for them to use  in their API calls.
    def make_new_token(self, user) :
        self.logger.log_event(self.logclient, "CREATE ACCESS TOK", 'a', ['Username'], user)
        tokcreate = datetime.datetime.now()
        tokexpire = tokcreate + timedelta(days=7)
        tc_str = self.dt_to_str(tokcreate)
        te_str = self.dt_to_str(tokexpire)

        salt = uuid.uuid4().hex
        token = hashlib.sha512(salt + tc_str).hexdigest()
        tokvals = [("val", token), ("user", user), ("created_at", tc_str), ("expires_at", te_str)]

        if self.dbutil.insert(self.ndbTokens, tokvals) :
            self.logger.log_event(self.logclient, "CREATE ACCESS TOK", 's', ['Username'], user)
            return token
        else :
            self.logger.log_event(self.logclient, "CREATE ACCESS TOK", 'f', ['Username'], user)
            return None

    # @info - every once in a while we need to go through and delete old tokens from the database
    #         this will look at each token expiration date and delete it if it's passed the current datetime.
    def clean_expired_tokens(self) :
        pass #@TODO

        

    def dt_to_str(self, dt) :
        return dt.strftime("%Y-%m-%d %H:%M:%S")

