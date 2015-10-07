#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

from unit_test import *
from vm_util import *
from auth_util import *

# @info - Unit testing suite for the auth util class which handles all user authentication
#         for the shared resource server.

class authUnitTest(UnitTest) :

    def __init__(self, vmargs, authargs, testargs) :
        self.title = 'Authorization Util'
        self.logger = testargs['logutil']
        self.logclient = testargs['logclient']
	self.schema = testargs['schema']
	self.dbname = self.schema['dbname']
        self.head_data=['Schema File : %s' % self.schema['file']] # Add info to log at top of test log file here
        self.tail_data=[] # ^^ bottom of test file here

        UnitTest.__init__(self, testargs)
	
        self.vmutil = vmUtil(vmargs)
        self.dbutil = authargs['dbutil']
        self.authutil = authUtil(authargs)

	self.drop_test_databases([self.dbname])

    def drop_test_databases(self, names) :
        for name in names :
            if self.dbutil.database_exists(name) :
                self.logger.log_event(self.logclient, 'INITIALIZATION', 'a',
                                     ['Database Drop'], name,  '( Already Exists )')
                if self.dbutil.drop_database(name) :
                    self.logger.log_event(self.logclient, 'INITIALIZATION', 's',
                                         ['Database Drop'], name, 'Continuing Test' )
                else :
                    self.logger.log_event(self.logclient, 'INITIALIZATION', 'f',
                                         ['Database Drop'], name, 'Ending Test' )
                    sys.exit(1)
        return True

    def drop_table(self, name) :
        cur = self.db.cursor()
        cur.execute('''SHOW TABLES LIKE '%s' ''' % name)
        if cur.fetchall() :
            cur.execute('''DELETE FROM %s'''%name)
            self.db.commit()


    def run(self) :
	ret = True
	ret = ret and self.build_test_database()
	ret = ret and self.test_add_users()
	ret = ret and self.test_get_users_token()
	ret = ret and self.test_get_users_auth_level()
        ret = ret and self.test_verify_users_auth_level()
	# ret = ret and self.drop_test_database()
	self.logtail(ret)
	return ret


    def build_test_database(self) :
	desc = "Building the test Database"
	self.logteststart(sys._getframe().f_code.co_name, desc)
	return self.maintest(sys._getframe().f_code.co_name, desc, self.dbutil.build_database(self.schema))

    def test_add_users(self) :
	desc = "Add a single user to the Users table."
	self.logteststart(sys._getframe().f_code.co_name, desc)

	TESTUSER = 'testuser'
	TESTHASH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	TESTEMAIL = 'test@test.com'
        TESTAUTH = 2

	TESTUSER2 = 'noobuser'
	TESTHASH2 = 'ABCDDDDDDDDIJKLMNOPQRSTUVWXYZ'
	TESTEMAIL2 = 'peaches@test.com'
        TESTAUTH2 = 1

	userargs = {'username' : TESTUSER,
		    'pwhash'   : TESTHASH,
		    'email'    : TESTEMAIL,
		    'auth'     : TESTAUTH}
	userargs2 = {'username' : TESTUSER2,
		    'pwhash'   : TESTHASH2,
		    'email'    : TESTEMAIL2,
		    'auth'     : TESTAUTH2}

	res = True

        # first user
	tok = self.authutil.create_user(userargs)
	res = res and self.subtest(sys._getframe().f_code.co_name, "Testing Token Returned From Create User", tok != None)

	res = res and self.authutil.check_user_exists(TESTUSER)
	self.subtest(sys._getframe().f_code.co_name, "Checking Added User Exists in DB", res)

	user_map = self.authutil.get_user(TESTUSER)
	res =  res and self.maintest(sys._getframe().f_code.co_name, desc, user_map != None)

        # second user
	tok = self.authutil.create_user(userargs2)
	res = res and self.subtest(sys._getframe().f_code.co_name, "Testing Token Returned From Create User", tok != None)

	res = res and self.authutil.check_user_exists(TESTUSER2)
	self.subtest(sys._getframe().f_code.co_name, "Checking Added User Exists in DB", res)

	user_map = self.authutil.get_user(TESTUSER2)
	return res and self.maintest(sys._getframe().f_code.co_name, desc, user_map != None)

    def test_get_users_token(self) :
	desc = "Get a Token for the User Just Added"
	self.logteststart(sys._getframe().f_code.co_name, desc)

	TESTUSER = 'testuser'
	TESTHASH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	TESTEMAIL = 'test@test.com'
        TESTAUTH = 2

	TESTUSER2 = 'noobuser'
	TESTHASH2 = 'ABCDDDDDDDDIJKLMNOPQRSTUVWXYZ'
	TESTEMAIL2 = 'peaches@test.com'
        TESTAUTH2 = 1

	userargs = {'username' : TESTUSER,
		    'pwhash'   : TESTHASH,
		    'email'    : TESTEMAIL,
		    'auth'     : TESTAUTH}
	userargs2 = {'username' : TESTUSER2,
		    'pwhash'   : TESTHASH2,
		    'email'    : TESTEMAIL2,
		    'auth'     : TESTAUTH2}
	res = True
        # first user
	res = res and self.authutil.check_user_exists(TESTUSER)
	self.subtest(sys._getframe().f_code.co_name, "Checking Added User Exists in DB", res)

	tok = self.authutil.get_token(TESTUSER)
	res = res and self.maintest(sys._getframe().f_code.co_name, desc, tok != None)

        # second user
	res = res and self.authutil.check_user_exists(TESTUSER2)
	self.subtest(sys._getframe().f_code.co_name, "Checking Added User Exists in DB", res)

	tok = self.authutil.get_token(TESTUSER2)
	return res and self.maintest(sys._getframe().f_code.co_name, desc, tok != None)

    def test_get_users_auth_level(self) :
        desc = "Get the newly added user's auth level"
	TESTUSER = 'testuser'
        TESTAUTH = 2
	TESTUSER2 = 'noobuser'
        TESTAUTH2 = 1
	res = True

	res = res and self.authutil.check_user_exists(TESTUSER)
        level = self.authutil.get_auth_level(TESTUSER)
        res = (level == TESTAUTH)
	res = res and self.maintest(sys._getframe().f_code.co_name, desc, res)

	res = res and self.authutil.check_user_exists(TESTUSER2)
        level = self.authutil.get_auth_level(TESTUSER2)
        res = (level == TESTAUTH2)
	return res and self.maintest(sys._getframe().f_code.co_name, desc, res)

    def test_verify_users_auth_level(self) :
        desc = "Test the verify_auth_level Function for the new user."
	TESTUSER = 'testuser'
        TESTAUTH = 2
	TESTUSER2 = 'noobuser'
        TESTAUTH2 = 1

	res = True

	res = res and self.authutil.check_user_exists(TESTUSER)
        res = res and self.subtest(sys._getframe().f_code.co_name, "Test Auth Level 0", self.authutil.verify_auth_level(TESTUSER, 0))
        res = res and self.subtest(sys._getframe().f_code.co_name, "Test Auth Level 1", self.authutil.verify_auth_level(TESTUSER, 1))
        res = res and self.subtest(sys._getframe().f_code.co_name, "Test Auth Level 2", self.authutil.verify_auth_level(TESTUSER, 2))
	res = res and self.maintest(sys._getframe().f_code.co_name, desc, res)

	res = res and self.authutil.check_user_exists(TESTUSER2)
        res = res and self.subtest(sys._getframe().f_code.co_name, "Test Auth Level 0", self.authutil.verify_auth_level(TESTUSER2, 0))
        res = res and self.subtest(sys._getframe().f_code.co_name, "Test Auth Level 1", self.authutil.verify_auth_level(TESTUSER2, 1))
        res = res and self.subtest(sys._getframe().f_code.co_name, "Test Auth Level 2", not self.authutil.verify_auth_level(TESTUSER2, 2))
	return res and self.maintest(sys._getframe().f_code.co_name, desc, res)

    def drop_test_database(self) :
	desc = "Dropping the test Database"
	self.logteststart(sys._getframe().f_code.co_name, desc)
	return self.maintest(sys._getframe().f_code.co_name, desc, self.dbutil.drop_database(self.dbname))

    
    
