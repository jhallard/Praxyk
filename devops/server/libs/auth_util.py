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
        self.ndbAuth = "Auth"

        # user auth defines, 3 levels going from read-only priviledges to root.
        self.AUTH_LOW = 0  # can only login to instances created for them
        self.AUTH_MED = 1  # can make and login to instances and and  and delete only their own
        self.AUTH_ROOT = 2 # root baby root!

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
        auth = userargs.get('auth', self.AUTH_LOW)

        vals = [("username", un), ("pwhash", pwhash), ("email", email)]

        if self.check_user_exists(un) :
            self.logger.log_event(self.logclient, "CREATE USER", "f", ['Username', 'Email'], (un, email), "User Already Exists in DB")
            return None 

        if self.dbutil.insert(self.ndbUsers, vals) : 
            self.logger.log_event(self.logclient, "CREATE USER", 's', ['Username', 'Email'], (un, email))
        else :
            self.logger.log_event(self.logclient, "CREATE USER", 'f', ['Username', 'Email'], (un, email))
            return None

        valsauth = [("username", un), ("level", auth)]

        if self.dbutil.insert(self.ndbAuth, valsauth) : 
            self.logger.log_event(self.logclient, "CREATE USER AUTH", 's', ['Username', 'Auth'], (un, str(auth)))
        else :
            self.logger.log_event(self.logclient, "CREATE USER AUTH", 'f', ['Username', 'Auth'], (un, str(auth)))
            return None

        return  self.make_new_token(un)

    # @info - updates a currently existing user in the database. The only attributes that can be updated are a users password 
    #         and email, the username cannot be changed, neither can the auth level.
    def update_user(self,userargs) :
        un = userargs['username']


        if not self.check_user_exists(un) :
            return self.logger.log_event(self.logclient, "UPDATEUSER", "f", ['Username', 'Email'], (un, email), "User Doesn't Exist in DB")
        user = self.get_user(un)

        
        pwhash = userargs.get('pwhash', user['pwhash'])
        email = userargs.get('email', user["email"])
        if not email :
            email = user['email']
        if not pwhash :
            pwhash = user['pwhash']
        vals = [("username", un), ("pwhash", pwhash), ("email", email)]
        if self.dbutil.update(self.ndbUsers, vals, "username='%s'"%str(un)) : 
            return self.logger.log_event(self.logclient, "UPDATE USER", 's', ['Username', 'Email'], (un, email))
        else :
            return self.logger.log_event(self.logclient, "UPDATE USER", 'f', ['Username', 'Email'], (un, email))
        

    # @info - ensures that a given token exists in the token database
    def validate_token(self, tok) :
        self.logger.log_event(self.logclient, "TOKEN VALIDATE", 'a')
        results = self.dbutil.query(self.ndbTokens, 'val, user', "val='%s'"%tok, "created_at ASC", limit=1)
        ret = None if not results else (len(results) >= 1)
        if not ret :
            return self.logger.log_event(self.logclient, "TOKEN VALIDATE", 'f')
        return results[0][1] # return the user name


    # @info - takes a username and a pwhash and validates that the credential are correct. 
    #         normally only used to get validate a user when their token expires and they
    #         need a new one.
    def validate_user(self, username, pwhash) :
        self.logger.log_event(self.logclient, "USER VALIDATE", 'a', ['User'], (username))
        user = self.get_user(username)
        ret = (user is not None and pwhash == user['pwhash'])
        return self.logger.log_event(self.logclient, "USER VALIDATE", 's' if ret else 'f', ['User'], (username))

    # @info - takes a user and gets a valid token for them. If none are available it makes a new one and returns
    #         it. This is called after the validate_user function is called.
    def get_token(self, user) :
        if not self.check_user_exists(user) :
            return self.logger.log_event(self.logclient, "TOKEN FETCH", 'f', ['User'], (user), "User Doesn't Exist")

        tok = self.dbutil.query(self.ndbTokens, '*', "user='%s'"%user, order_by="created_at ASC", limit=1)

        if not tok or not tok[0] :
            self.logger.log_event(self.logclient, "TOKEN FETCH", 'f', ['User'], (user), "No Tokens Found")
            return None
        else :
            expires_at = tok[0][3]
            if self.dt_to_str(expires_at) <  self.dt_to_str(datetime.datetime.now()) :
                return self.make_new_token(user)
            else :
                return tok[0][0] # the token value

    # @info - get a users attributes from the database base on the username
    def get_user(self, username) :
        if not self.check_user_exists(username) :
            self.logger.log_event(self.logclient, "USER INFO FETCH", 'f', ['User'], (username), "User Doesn't Exist")
            return {}
        user = self.dbutil.query(self.ndbUsers, '*', "username='%s'"%username, limit=1)

        if user :
            user = user[0] # it's the first and only row returned.

        auth = self.get_auth_level(username)
        if user and len(user) >= 3 : 
            return {'username' : user[0], 'pwhash' : user[1], 'email' : user[2], 'auth' : auth}
        else :
            return {}

    # @info - gets the auth level for the given user from the database and returns it
    def get_auth_level(self, username) :
        if not self.check_user_exists(username) :
            return self.logger.log_event(self.logclient, "USER AUTH FETCH", 'f', ['User'], (username), "User Doesn't Exist")

        auth = self.dbutil.query(self.ndbAuth, 'level', "user='%s'"%username, limit=1)

        if auth :
            self.logger.log_event(self.logclient, "USER AUTH FETCH", 's', ['User', 'Auth Level'],
                                  (username, str(auth[0][0])))
            return auth[0][0]
        return None

    # @info - makes sure that the given users auth level is at or below the given level
    def verify_auth_level(self, username, auth_level) :
        self.logger.log_event(self.logclient, "VERIFY AUTH", 'a', ['User', 'Auth Level'], (username, str(auth_level)))
        user = self.get_user(username)

        if not username :
            return self.logger.log_event(self.logclient, "VERIFY AUTH", 'f', ['User', 'Auth Level'], (username, str(auth_level)),
                                         "User Doesn't Exist")

        verified = (user['auth'] >= auth_level)
        return self.logger.log_event(self.logclient, "VERIFY AUTH", 's' if verified else 'f', ['User'], (username))



    # @info - make a new valid token for the user, put it in the database, and return the token
    #         for them to use  in their API calls.
    def make_new_token(self, user) :
        self.logger.log_event(self.logclient, "CREATE ACCESS TOK", 'a', ['Username'], user)
        tokcreate = datetime.datetime.now()
        tokexpire = tokcreate + timedelta(days=1)
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

