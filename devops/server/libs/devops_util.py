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

        self.regions = ['sfo1', 'nyc1', 'nyc2']
        self.providers = ['DO', 'AWS', 'GCE']

        # Table names for the devops database
        self.ndbUsers = "Users"
        self.ndbTokens = "Tokens"
        self.ndbInstances = "Instances"
        self.ndbAdmin = "Admin"
        self.ndbSnapshots = "Snapshots"
        self.ndbImages = "Images"
        self.ndbProviders = "Providers"
        self.ndbSSHKeys = "SSHKeys"
        self.ndbRegions = "Regions"

    # @info - uses the dbUtil class to build the database that contains all of the devops info,
    #         like users, token, admin rights, instances, etc.
    def build_database(self) :
        self.logger.log_event(self.logclient, "BUILDING DATABASE", 'a', ['DB Name'], self.dbname)

        if self.dbutil.database_exists(self.dbname) :
            return self.logger.log_event(self.logclient, "BUILDING DATABASE", 'f', ['DB Name'], self.dbname,
                                         "DB Already Exists, must drop before rebuilding.")

        ret = self.dbutil.build_database(self.schema)
        return self.logger.log_event(self.logclient, "BUILDING DATABASE", ('s' if ret else 'f'),
                                     ['DB Name'], self.dbname)

    # @info - this fills the database created in self.build_database by grabbing the current instances
    #         and the root user and adding them to the db along with a root token. After this is called
    #         the root user can make other users.
    def fill_database(self) :
        self.logger.log_event(self.logclient, "FILLING DATABASE", 'a', ['DB Name'], self.dbname)
        
        # start by making the root user given to us in the config file
        userargs = {'username' : self.rootuser,
                    'pwhash' : self.rootpwdhash,
                    'email' : self.rootemail}

        create_user_res = self.authutil.create_user(userargs)

        if not create_user_res :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                         ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                         "Could not add Root User to DB")
        else :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 's',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Root User Added to DB")

        if not self.add_regions() :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Couldn't Add Instance Regions to DB")

        if not self.add_providers() :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Couldn't Add IaaS Providers to DB")

        if not self.add_boot_images() :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Couldn't Add Boot Images to DB")


        # then add in any existing digital ocean instances.
        instances = self.vmutil.get_vm_instances()

        if not instances :
            instances = [] # it's okay if no instances are running, we just have nothing to insert

        create_inst_res = True
        for inst in instances :
            create_inst_res = create_inst_res and self.add_instance_db(inst, self.rootuser)

        if not create_inst_res :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'i',
                                     ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                     "Could not add All Instances to DB")

        if not self.add_snapshots() :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 'i',
                                         ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                         "Could not Add All Snapshots to DB")





    # @info - adds a VM instance to the database. Takes in an instance (returned from get_vm_instance
    #         in vmUtil) and a creator (username of the caller) and puts the new instance in the db.
    def add_instance_db(self, instance, creator) :
        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'a', 
                              ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                              (self.dbname, instance.name, instance.id, creator))

        (instance, imgs, keys) = self.vmutil.format_do_instance(instance, self.rootuser)

        if not instance :
            return self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', 
                                  ['DB Name', 'Creator'], (self.dbname, creator),
                                  "Instance Could not be Formatted Correctly.")

        if not self.dbutil.insert(self.ndbInstances, instance) :
            return self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', 
                                  ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                                  (self.dbname, instance[1], instance[0], creator),
                                  "DB Insert Failed, check DB Logs.")
        else :
            self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 's', 
                                  ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                                  (self.dbname, instance[1], instance[0], creator),
                                  "Instance Added to DB.")
        if imgs :
            for xid in imgs[0][1]:
                snap = self.vmutil.get_snapshot(xid)
                if not snap :
                    self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', 
                                      ['DB Name', 'Instance Name', 'Instance ID', 'Creator', 'Snapshot ID'],
                                      (self.dbname, instance[1], instance[0], creator, xid),
                                      "Could not get Snapshot object from IaaS API")
                else :
                    snapshot = self.vmutil.format_snapshot(snap, instance[1])
                    if self.dbutil.insert_or_update(self.ndbSnapshots, snapshot) :
                        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 's', ['Snapshot ID', 'Instance ID'], 
                                              (xid, instance[1]), "Snapshot Added to DB")
                    else :
                        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', ['Snapshot ID', 'Instance ID'], 
                                              (xid, instance[1]), "Snapshot Added to DB")
        if keys :
            pass

        return True



    # @info - adds the available instance regions to the db
    def add_regions(self) :
        self.logger.log_event(self.logclient, "ADDING REGIONS", 'a', [], "")
        ret = True
        for region in self.regions :
            ret = ret and self.dbutil.insert(self.ndbRegions, [("slug", str(region))])
        self.logger.log_event(self.logclient, "ADDING REGIONS", ('s' if ret else 'f'), [], "")
        return ret

    # @info - adds the IaaS providers we use to the db
    def add_providers(self) :
        self.logger.log_event(self.logclient, "ADDING PROVERSS", 'a', [], "")
        ret = True
        for provider in self.providers :
            ret = ret and self.dbutil.insert(self.ndbProviders, [("slug", str(provider))])
        self.logger.log_event(self.logclient, "ADDING PROVIDERS", ('s' if ret else 'f'), [], "")
        return ret

    # @info - adds the default boot images to the db (ex ubuntu-14.04-x64, etc.)
    def add_boot_images(self) :
        self.logger.log_event(self.logclient, "ADDING BOOT IMAGES", 'a')

        imgs = self.vmutil.get_boot_images() 

        if not imgs :
            return self.logger.log_event(self.logclient, "ADDING BOOT IMAGES", 'f', [], "", "Boot Images List Came Back Empty.")
        ret = True
        for img in imgs :
            ret = ret and self.dbutil.insert(self.ndbImages, img)

        return self.logger.log_event(self.logclient, "ADDING BOOT IMAGES", 's' if ret else 'f', ['Num Images'], len(imgs))

    # @info - grabs any existing snapshots and adds them to the database
    def add_snapshots(self) :
        self.logger.log_event(self.logclient, "ADDING EXISTING SNAPSHOTS", 'a')

        snapshots = self.vmutil.get_snapshots()
        if not snapshots :
            self.logger.log_event(self.logclient, "ADDING EXISTING SNAPSHOTS", 's', ['Num Snapshots'], '0')
            return True

        ret = True
        for snapshot in snapshots :
            ret = ret and self.dbutil.insert(self.ndbSnapshots, snapshot) 

        return self.logger.log_event(self.logclient, "ADDING EXISTING SNAPSHOTS", 's' if ret else 'f', ['Num Snapshots'], len(snapshots))


    # @info - takes a dictionary {'name' : 'value'} and formats it into the list of tuples [('name', 'value') ...]
    #         that is needed to insert into the db with the dbUtil class
    def format_db(self, vals) :
        if not vals :
            return []
        ret = []
        for key,val in vals.items() :
            ret.append((key, str(val)))
        return ret


    # @info - util to hash and salt the users password for storage in the db
    def hashpw(self, user, pw) :
        salt = pw[0] + user[0] +  'sss' + user + pw[1]*3 + 'ttt' + user[1] +  pw[2] + pw[1]
        return hashlib.sha512(salt + pw).hexdigest()






