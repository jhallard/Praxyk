#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

# @info - Unit testing suite for the auth util class which handles all user authentication
#         for the shared resource server.
from unit_test import *
from vm_util import *
from auth_util import *
from devops_util import *

class devopsUnitTest(UnitTest) :

    def __init__(self, dbargs, vmargs, authargs, devopsargs, testargs) :
        self.title = 'DevOps Util'
        self.logger = testargs['logutil']
        self.logclient = testargs['logclient']
	self.schema = testargs['schema']
	self.dbname = self.schema['dbname']
        self.flags = testargs.get('flags', 'a')
	if not self.flags :
	    self.flags = "a"
        self.head_data=['Schema File : %s' % self.schema['file']] # Add info to log at top of test log file here
        self.tail_data=[] # ^^ bottom of test file here

        UnitTest.__init__(self, testargs)
	
        self.dbutil = dbUtil(dbargs)
        self.dbutil.login()
        self.rootuser = devopsargs['rootuser']
        self.rootkey = devopsargs['sshkey']
        self.devopsutil = devopsUtil(dbargs, vmargs, authargs, devopsargs)
        self.authutil = self.devopsutil.authutil

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

        if 'a' in self.flags :
            ret = ret and self.test_build_database()
            ret = ret and self.test_fill_database()
            # ret = ret and self.test_add_user()
            # ret = ret and self.test_create_instance_root()
            # ret = ret and self.test_create_instance_user()
            # ret = ret and self.test_get_user()
            # ret = ret and self.test_get_user_token()
            # ret = ret and self.test_drop_database()

	self.logtail(ret)
	return ret

	# ret = ret and self.test_build_database()
        # ret = ret and self.test_fill_database()
	# ret = ret and self.test_add_user()
	# ret = ret and self.test_get_user_token()
	# ret = ret and self.test_drop_database()

    def test_add_user(self) :
        desc = "Adding a single new user to the database"
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
                    

        create_user_res = self.authutil.create_user(userargs)
	self.user_token1 = create_user_res
	self.maintest(sys._getframe().f_code.co_name, desc, create_user_res is not None)

        create_user_res = self.authutil.create_user(userargs2)
	self.user_token1 = create_user_res
        return	self.maintest(sys._getframe().f_code.co_name, desc, create_user_res is not None)


    def test_create_instance_root(self) :
        desc = "Creating a single instance, checking it's live and adding it to the DB."
	self.logteststart(sys._getframe().f_code.co_name, desc)

        vmargs = { 'name' : 'TEST-INST-ALPH',
                   'region' : 'sfo1',
                   'image'  : 'ubuntu-14-04-x64',
                   'class'  : '1gb'
                   }

        res = self.devopsutil.create_vm_instance(self.rootuser, vmargs)
	return self.maintest(sys._getframe().f_code.co_name, desc, res)

    def test_create_instance_user(self) :
        desc = "Creating a single instance, checking it's live and adding it to the DB."
	self.logteststart(sys._getframe().f_code.co_name, desc)
	TESTUSER = 'testuser'
	TESTHASH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	TESTEMAIL = 'test@test.com'
        TESTAUTH = 2

        vmargs = { 'name' : 'TEST-INST-BETA',
                   'region' : 'sfo1',
                   'image'  : 'ubuntu-14-04-x64',
                   'class'  : '2gb'
                   }

        res = self.devopsutil.create_vm_instance(TESTUSER, vmargs)
	return self.maintest(sys._getframe().f_code.co_name, desc, res)

    def test_get_user(self) :
        desc = "Creating a single instance, checking it's live and adding it to the DB."
	self.logteststart(sys._getframe().f_code.co_name, desc)
        user = self.devopsutil.get_user("root")
	return self.maintest(sys._getframe().f_code.co_name, desc, user is not None)

    def test_build_database(self) :
	desc = "Building the test Database"
	self.logteststart(sys._getframe().f_code.co_name, desc)
	return self.maintest(sys._getframe().f_code.co_name, desc, self.devopsutil.build_database())

    def test_fill_database(self) :
	desc = "Filling the test Database"
	self.logteststart(sys._getframe().f_code.co_name, desc)
	return self.maintest(sys._getframe().f_code.co_name, desc, self.devopsutil.fill_database())


    def test_drop_database(self) :
	desc = "Dropping the test Database"
	self.logteststart(sys._getframe().f_code.co_name, desc)
	return self.maintest(sys._getframe().f_code.co_name, desc, self.dbutil.drop_database(self.dbname))

    
    
