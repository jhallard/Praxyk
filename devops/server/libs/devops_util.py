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
        self.rootkey = devopsargs['sshkey']

        self.dbutil.use_database(self.dbname)

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

    ########## SSH Keys ##########

    # @info - adds an ssh key to both the registered ssh key lists for the various service providers
    #         and adds it to the database for our own tracking purposes.
    def add_ssh_key(self, user, keyname, keyargs) :
        self.logger.log_event(self.logclient, "ADD NEW SSHKEY", 'a', ['User', 'Keyname'], (user, keyname))
        keyargs['name'] = keyname
        newkey = self.vmutil.add_ssh_key(keyargs)
        if not newkey :
            return self.logger.log_event(self.logclient, "ADD NEW SSHKEY", 'f', ['User', 'Keyname'], (user, keyname))
        else :
            self.logger.log_event(self.logclient, "ADD NEW SSHKEY", 'i', ['User', 'Keyname'], (user, keyname), "Added to IaaS Providers")

        key_formatted = self.vmutil.format_ssh_key(newkey, user)

        res = self.dbutil.insert(self.ndbSSHKeys, key_formatted)
        self.logger.log_event(self.logclient, "ADD NEW SSHKEY", 's' if res else 'f', ['User', 'Keyname'],
                              (user, keyname), "Added to IaaS Providers")

        return newkey

    ########## VM Instances ##########

    # @info - creates a new virtual machine with the user's SSH keys added 
    def create_vm_instance(self, user, vmargs) :
        self.logger.log_event(self.logclient, "CREATE NEW INSTANCE", 'a', ['User', 'VM Name'], (user, vmargs['name']))
        ssh_keys = self.get_ssh_keys(user)
        droplet = self.vmutil.create_vm_instance(vmargs, ssh_keys)

        if not droplet :
            self.logger.log_event(self.logclient, "CREATE NEW INSTANCE", 'f', ['User', 'VM Name'], (user, vmargs['name']))
            return None
        else :
            self.logger.log_event(self.logclient, "CREATE NEW INSTANCE", 's', ['User', 'VM Name'], (user, vmargs['name']))

        active = self.vmutil.wait_for_state(droplet.id, ['active'], 180)
        if active : # to propagate the updated state
            droplet = self.vmutil.get_vm_instance(droplet.id)

        result = self.add_instance_db(droplet, user)
        self.logger.log_event(self.logclient, "CREATE NEW INSTANCE", 's' if result else 'f', ['User', 'VM Name'],
                              (user, vmargs['name']))

        return droplet

    # @info - deletes the vm-instance with the given ID
    def delete_vm_instance(self, xid) :
        self.logger.log_event(self.logclient, "DELETE INSTANCE", 'a', ['VM ID'], str(xid))

        if not self.get_vm_instances(xid) :
            return self.logger.log_event(self.logclient, "DELETE INSTANCE", 'f', ['VM ID'], str(xid), "Instance not Found.")

        if not self.vmutil.destroy_vm_instance(xid) :
            return self.logger.log_event(self.logclient, "DELETE INSTANCE", 'f', ['VM ID'], str(xid), "Instance Destroy Call Failed")

        ret = self.dbutil.delete(self.ndbInstances, "id='%s'"%str(xid))

        return ret

    # @info - returns a list of dictionaries that completely describe all of the instances if xid is not given
    #         else only returns that instance given by the xid. 
    #         Instances returned are formatted for the API.
    def get_vm_instances(self, xid=None) :
        if not xid :
            instances = self.dbutil.query(self.ndbInstances, "*")
        else :
            instances = self.dbutil.query(self.ndbInstances, "*", "id='%s'"%xid, limit=1)
        ret = []

        for inst in instances :
            formatted = { 
                "id"     : inst[0],
                "name"   : inst[1],
                "image"  : inst[2],
                "ip"     : inst[3],
                "class"  : inst[5],
                "disk"   : inst[6],
                "status" : inst[8],
                "creator" :inst[9],
                "created_at" : str(inst[10]),
            }
            ret.append(formatted)
        return ret


    ########## SNAPSHOTS ##########
    # @info - creates a new virtual machine with the user's SSH keys added 
    def create_vm_snapshot(self, inst_id, snap_name, description="") :
        self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 'a', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name))

        if self.dbutil.query(self.ndbSnapshots, '*', "name='%s'"%snap_name, limit=1) :
            self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 'f', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name),
                                  "A snapshot with that name already exists in the database, names must be unique.")
            return None
        snap_action = self.vmutil.create_vm_snapshot(inst_id, snap_name)

        if not snap_action :
            self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 'f', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name))
            return None
        else :
            self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 's', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name))

        snap_action.wait(5)

        inst_name = self.dbutil.query(self.ndbInstances, 'name', "id='%s'"%inst_id)

        if inst_name :
            inst_name = inst_name[0][0]
        else :
            inst_name = ""
        
        snapshot = self.vmutil.get_snapshot_by_name(snap_name, inst_name=inst_name, desc=description)

        if not snapshot :
            self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 'f', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name),
                                  "get_snapshot_by_name call failed after snapshot creation.")
            return None

        if not self.dbutil.insert(self.ndbSnapshots, snapshot) :
            self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 'f', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name), 
                                  "Insert Snapshot into DB Failed.")
            return None
            
        self.logger.log_event(self.logclient, "CREATE NEW SNAPSHOT", 's', ['Inst ID', 'Snapshot Name'], (inst_id, snap_name))

        find_new_snap = self.get_vm_snapshots(snapshot[1][1]) # format the snapshot for the api
        if find_new_snap :
            return find_new_snap[0]
        else :
            return None

    # @info - returns a list of dictionaries that completely describe the requested snapshot(s). This function
    #         can be called with no arguments, in which case all snapshots are grabbed, or it can be called with
    #         a snapshot id to only return that one specific snapshot as the element of a list.
    def get_vm_snapshots(self, xid=None) :
        if not xid :
            snapshots = self.dbutil.query(self.ndbSnapshots, "*")
        else :
            snapshots = self.dbutil.query(self.ndbSnapshots, "*", "id='%s'"%xid, limit=1)
        ret = []

        for snap in snapshots :
            formatted = { 
                "name"       : snap[0],
                "id"         : snap[1],
                "inst_name"  : snap[2],
                "created_at" : str(snap[3]),
                "description": snap[5],
            }
            ret.append(formatted)
        return ret

    # @info - gets a users info - the name, email, and current running instances.
    def get_user(self, username) :
        instances = self.get_vm_instances()
        users_instances = [inst['id'] for inst in instances if inst['creator'] == username]
        user = self.authutil.get_user(username)
        if user :
            return {'username' : user['username'], 'email' : user['email'], 'instances' : users_instances}
        else :
            return {}


    # @info - gets all users info - the name, email, and current running instances.
    def get_users(self) :
        users = self.dbutil.query(self.ndbUsers, 'username')
        users_list = []
        for user in users :
            user = self.get_user(user[0])
            users_list.append(user)
        return users_list

    # @info - add a user to the database
    def create_user(self, userargs) :
        return self.authutil.create_user(userargs)

    # @info - upfate an existing user with new info, can only change password and email address for user.
    def update_user(self, userargs) :
        return self.authutil.update_user(userargs)

    
    # @info - get all of the ssh keys from the database for either one user or all of them (Depending on user argument)
    def get_ssh_keys(self, user=None) :
        self.logger.log_event(self.logclient, "GET SSH KEYS", 'a', ['User'], (user if user else "All"))
        if user :
            auth_level = self.authutil.get_auth_level(user)
            # keyids = self.dbutil.query(self.ndbSSHKeys, 'id', ""%user)
            keyids = self.dbutil.query("""(SSHKeys JOIN Auth ON (SSHKeys.user=Auth.user))""", 'SSHKeys.id', "Auth.level>='%s'"%auth_level)
        else :
            keyids = self.dbutil.query(self.ndbSSHKeys, 'id')

        self.logger.log_event(self.logclient, "GET SSH KEYS", 'f' if not keyids else 's',
                              ['User', 'Num Keys'], ( (user if user else "All"), str(len(keyids if keyids else '0')) ) )
        if keyids :
            return [int(key[0]) for key in keyids]
        else :
            return []


    # @info - gets the existing instances that the user has access to and returns their names, id's, 
    #         and ip addresses.
    def get_all_instances_do(self) :
        self.logger.log_event(self.logclient, "GET ALL INSTANCES", 'a')
        return self.vmutil.get_vm_instances(self)

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
                    'pwhash'   : self.rootpwdhash,
                    'email'    : self.rootemail,
                    'auth'     : self.authutil.AUTH_ROOT}

        userkeyargs = {'public_key' : self.rootkey['public_key'],
                       'fingerprint': self.rootkey['fingerprint']}

        create_user_res = self.authutil.create_user(userargs)

        if not create_user_res :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                         ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                         "Could not add Root User to DB")
        else :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 's',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Root User Added to DB")

        if not self.add_ssh_key(self.rootuser, self.rootkey['name'], userkeyargs) :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Failed to Add Root SSH Key")
        else :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Root SSH Key Added")

        if not self.add_existing_regions() :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Couldn't Add Instance Regions to DB")

        if not self.add_existing_providers() :
            self.logger.log_event(self.logclient, "FILLING DATABASE", 'f',
                                  ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                  "Couldn't Add IaaS Providers to DB")

        if not self.add_existing_boot_images() :
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

        if not self.add_existing_snapshots() :
            return self.logger.log_event(self.logclient, "FILLING DATABASE", 'i',
                                         ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                         "Could not Add All Snapshots to DB")

        return self.logger.log_event(self.logclient, "FILLING DATABASE", 's',
                                     ['DB Name', 'User Name'], (self.dbname, self.rootuser),
                                     "Database Filled")



    # @info - adds a VM instance to the database. Takes in an instance (returned from get_vm_instance
    #         in vmUtil) and a creator (username of the caller) and puts the new instance in the db.
    def add_instance_db(self, instance, creator) :
        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'a', 
                              ['DB Name', 'Instance Name', 'Instance ID', 'Creator'],
                              (self.dbname, instance.name, instance.id, creator))

        (instance, imgs, keys) = self.vmutil.format_do_instance(instance, creator)

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
                    # snap[2][1] = instance[1] # set the snapshot instance name to the added instance name
                    if self.dbutil.insert_or_update(self.ndbSnapshots, snap, "id='%s'"%str(xid)) :
                        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 's', ['Snapshot ID', 'Instance ID'], 
                                              (xid, instance[1]), "Snapshot Added to DB")
                    else :
                        self.logger.log_event(self.logclient, "ADDING VM INSTANCE", 'f', ['Snapshot ID', 'Instance ID'], 
                                              (xid, instance[1]), "Snapshot Added to DB")

        return True



    # @info - adds the available instance regions to the db
    def add_existing_regions(self) :
        self.logger.log_event(self.logclient, "ADDING REGIONS", 'a', [], "")
        ret = True
        for region in self.regions :
            ret = ret and self.dbutil.insert(self.ndbRegions, [("slug", str(region))])
        self.logger.log_event(self.logclient, "ADDING REGIONS", ('s' if ret else 'f'), [], "")
        return ret

    # @info - adds the IaaS providers we use to the db
    def add_existing_providers(self) :
        self.logger.log_event(self.logclient, "ADDING PROVERSS", 'a', [], "")
        ret = True
        for provider in self.providers :
            ret = ret and self.dbutil.insert(self.ndbProviders, [("slug", str(provider))])
        self.logger.log_event(self.logclient, "ADDING PROVIDERS", ('s' if ret else 'f'), [], "")
        return ret

    # @info - adds the default boot images to the db (ex ubuntu-14.04-x64, etc.)
    def add_existing_boot_images(self) :
        self.logger.log_event(self.logclient, "ADDING BOOT IMAGES", 'a')

        imgs = self.vmutil.get_boot_images() 

        if not imgs :
            return self.logger.log_event(self.logclient, "ADDING BOOT IMAGES", 'f', [], "", "Boot Images List Came Back Empty.")
        ret = True
        for img in imgs :
            ret = ret and self.dbutil.insert(self.ndbImages, img)

        return self.logger.log_event(self.logclient, "ADDING BOOT IMAGES", 's', ['Num Images'], len(imgs))

    # @info - grabs any existing snapshots and adds them to the database
    def add_existing_snapshots(self) :
        self.logger.log_event(self.logclient, "ADDING EXISTING SNAPSHOTS", 'a')

        snapshots = self.vmutil.get_snapshots()
        if not snapshots :
            self.logger.log_event(self.logclient, "ADDING EXISTING SNAPSHOTS", 's', ['Num Snapshots'], '0')
            return True

        ret = True
        for snapshot in snapshots :
            ret = ret and self.dbutil.insert(self.ndbSnapshots, snapshot) 

        return self.logger.log_event(self.logclient, "ADDING EXISTING SNAPSHOTS", 's', ['Num Snapshots'], len(snapshots))


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






