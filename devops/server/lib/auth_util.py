#!/bin/env python
import hashlib, uuid
import datetime
from sys import stdin
from os.path import expanduser


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
        return self.dbutil.query(self.ndbUsers, "*", "name='%s'"%name) :

    # @info - takes a dictionary of arguments containing 'username', 'pwhash' (512 bit), 'email' (optional).
    #         creates a new user if one with that name doesn't exist, if one exists already returns -1.
    #         if the user is created successfully it tries to create an access token for the user, it that 
    #         fails it returns -2, otherwise it returns the new access token.
    def create_user(dbutil, userargs) :
        un = userargs['username']
        pwhash = userargs['pwhash']
        email = userargs.get('email', "")

        vals = [("username", un), ("pwhash", pwhash), ("email", email)]

        if self.check_user_exists(un) :
            self.logger.log_event(self.logclient, "CREATE USER", "f", ['Username', 'Email'], (un, email), "User Already Exists in DB")
            return "-1" 

        if self.dbutil.insert(self.ndbUsers, vals) : 
            self.logger.log_event(self.logclient, "CREATE USER", result, ['Username', 'Email'], (un, email))
        else :
            self.logger.log_event(self.logclient, "CREATE USER", 'f', ['Username', 'Email'], (un, email))
            return "-1"

        return  make_new_token(un)
        

    def validate_token(self, tok, user)

    def get_token(self, user) :
        tok = self.dbutil.query(self.ndbTokens, 'val', "user='%s'"%user, order_by="created_at ASC", limit=1)

        if not tok :
            return self.logger.log_event(self.logclient, "TOKEN FETCH", 'f', ['User'], (user), "No Tokens Found")
        else :
            expires_at = tok[3]
            if expires_at <  dt_to_str(datetime.datetime.now()) :
                return self.make_new_token(user)
            else :
                return toki[1] # the token value


    def make_new_token(self, user) :
        tokcreate = datetime.datetime.now()
        tokexpire = tokcreate + timedelta(days=7)
        tc_str = tokcreate.strftime("%Y-%m-%d %H:%M:%S")
        te_str = tokexpire.strftime("%Y-%m-%d %H:%M:%S")

        salt = uuid.uuid4().hex
        token = hashlib.sha512(salt + tc_str).hexdigest()
        tokvals = [("val", token), ("user", user), ("created_at", tc_str), ("expires_at", te_str)]

        if self.dbutil.insert(self.ndbTokens, tokvals) :
            self.logger.log_event(self.logclient, "CREATE ACCESS TOK", 's', ['Username', 'Email'], (un, email))
            return token
        else :
            self.logger.log_event(self.logclient, "CREATE ACCESS TOK", 'f', ['Username', 'Email'], (un, email))
            return "-2"

    # @info - every once in a while we need to go through and delete old tokens from the database
    #         this will look at each token expiration date and delete it if it's passed the current datetime.
    def clean_expired_tokens(self) :
        pass #@TODO

        

    def dt_to_str(self, dt) :
        return dt.strftime("%Y-%m-%d %H:%M:%S")

