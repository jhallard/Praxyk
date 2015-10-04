#!/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import hashlib, uuid
import datetime
from datetime import timedelta
from os.path import expanduser

from db_util import *
from vm_util import *
from log_util import *
from auth_util import *


# @info - This class provides all of the functions that the request handler can call (See devops_request_handler). 
#         It acts the combination between the vmUtil, authUtil, and dbUtil classes in that it manages VMs for 
#         authorized users and stores the relevant data in the devops database.
class devopsUtil :

    # @info - Takes 3 dictionaries : dbargs is a map of database args like user, name, ip. vmargs is a map of arguments
    #         needed to generate a vmUtil class. devopsargs are all the args needed to generate this class.
    def __init__(self, dbargs, vmargs, authargs, devopsargs) :
        self.dbutil = dbUtil(dbargs)
        self.dbutil.login()

        self.vmutil = vmUtil(vmargs)
        self.vmutil.login()

        authargs['dbutil'] = self.dbutil
        self.authutil = authUtil(authargs)

        self.logger = devopsargs['logutil']
        self.logclient = devopsargs['logclient']
        self.schema = devopsargs['schema']
        self.dbname = self.schema['dbname']
        self.rootuser = devopsargs['rootuser']
        self.rootpwdhash = self.hashpw(self.rootuser, devopsargs['rootpwd'])
        self.rootemail = devopsargs['rootemail']

        # Table names for the devops database
        self.ndbUsers = "Users"
        self.ndbTokens = "Tokens"
        self.ndbInstances = "Instances"
        self.ndbAdmin = "Admin"
        self.ndbSnapshots = "Snapshots"
        self.ndbImages = "Images"
        self.ndbProviders = "Providers"
        self.ndbSSHKeys = "SSHKeys"

    # @info - uses the dbUtil class to build the database that contains all of the devops info,
    #         like users, token, admin rights, instances, etc.
    def build_database(self) :
        self.logger.log_event(self.logclient, "BUILDING DATABASE", 'a', ['DB Name'], self.dbname)
        ret = self.dbutil.build_database(self.schema)
        return self.logger.log_event(self.logclient, "BUILDING DATABASE", ('s' if ret else 'f'),
                                     ['DB Name'], self.dbname)

    # @info - this fills the database created in self.build_database by grabbing the current instances
    #         and the root user and adding them to the db along with a root token. After this is called
    #         the root user can make other users.
    def fill_database(self) :
        self.logger.log_event(self.logclient, "FILLING DATABASE", 'a', ['DB Name'], self.dbname)

        instances = self.vmutil.get_vm_instances()

        if not instances :
            instances = [] # it's okay if no instances are running, we just have nothing to insert

        userargs = {'username' : self.rootuser,
                    'pwhash' : self.rootpwdhash,
                    'email' : self.rootemail}

        create_user_res = self.authutil.create_user(userargs)

        if not create_user_res :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                         ['DB Name', 'User Name'],
                                         (self.dbname, self.rootuser),
                                         "Could not add Root User to DB")
        else :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 's',
                                  ['DB Name', 'User Name'],
                                  (self.dbname, self.rootuser),
                                  "Root User Added to DB")

        create_inst_res = True
        for inst in instances :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'i',
                                  ['DB Name', 'User Name', 'Instance Name', 'Instance ID'],
                                  (self.dbname, self.rootuser, inst.name, inst.id),
                                  "Root User Added to DB")
            create_inst_res = create_inst_res and self.add_instance_db(inst, self.rootuser)

        if not create_inst_res :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                         ['DB Name', 'User Name'],
                                         (self.dbname, self.rootuser),
                                         "Could not add All Instances to DB")
        else :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 's',
                                         ['DB Name', 'User Name'],
                                         (self.dbname, self.rootuser),
                                         "All Instances Added to DB")





    # @info - adds a VM instance to the database. Takes in an instance (returned from get_vm_instance
    #         in vmUtil) and a creator (username of the caller) and puts the new instance in the db.
    def add_instance_db(self, instance, creator) :
        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'a', 
                              ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                              (self.dbname, instance.name, instance.id, creator))

        instance = self.vmutil.format_do_instance(instance)

        if not instance :
            return self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', 
                                  ['DB Name', 'Creator'],
                                  (self.dbname, creator),
                                  "Instance Could not be Formatted Correctly.")

        if not self.dbutil.insert(self.ndbInstances, self.format_db(instance)) :
            return self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', 
                                  ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                                  (self.dbname, instance['name'], instance['id'], creator),
                                  "DB Insert Failed, check DB Logs.")
        else :
            return self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 's', 
                                  ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                                  (self.dbname, instance['name'], instance['id'], creator),
                                  "Instance Added to DB.")



    def format_db(self, vals) :
        if not vals :
            return []
        ret = []
        for key,val in vals.items() :
            ret.append((key, str(val)))
        return ret


    def hashpw(self, user, pw) :
        # should be salted I know
        salt = pw[0] + user[0] +  'sss' + user + pw[1]*3 + 'ttt' + user[1] +  pw[2] + pw[1]
        return hashlib.sha512(salt + pw).hexdigest()






