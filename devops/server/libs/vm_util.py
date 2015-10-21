#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import digitalocean
import datetime
import socket
import time

# @info - This class acts as an interface between other scripts and the various IaaS APIs like
#         Digital Oceans and eventually GCE and AWS. It doesn't work a database at all, it simply
#         allows us to query, create, destroy, and otherwise manage VMs and snapshots of VMs that
#         are running with the configured IaaS providers
class vmUtil :

    def __init__(self, vmargs) :
        self.tok = vmargs['tok']
        self.logger = vmargs['logutil']
        self.logclient = vmargs['logclient']
        self.manager = None # will be filled on @login call
        socket.setdefaulttimeout(0.5)

    # @info - logs us in with the API wrapper libraries we are using to access the IaaS APIs
    def login(self, vendor="DO") :
        self.manager = digitalocean.Manager(token=self.tok)

        status = 'f' if not self.manager else 's'
        return self.logger.log_event(self.logclient, 'IAAS VENDOR LOGIN', status, ['Vendor'], vendor)

    # @info - gets all of the currently running VM instances from a specific IaaS vendor (default is dig. ocean)
    def get_vm_instances(self, vendor="DO") :
        self.logger.log_event(self.logclient, 'GET VM INSTANCES', 'a')
        if self.manager :
            try :
                droplets =  self.manager.get_all_droplets()
                self.logger.log_event(self.logclient, 'GET VM INSTANCES', 's', ['Vendor', 'Num Instances'], (vendor, len(droplets)))
                return droplets
            except Exception, e :
                self.logger.log_event(self.logclient, "GET VM INSTANCES", 'e', ['Vendor', 'e.what()'], (vendor, str(e)))
                return None
        else :
            self.logger.log_event(self.logclient, 'GET VM INSTANCES', 'f', ['Vendor'], vendor)
            return None

    # @info - gets the dictionary that represents a VM instance based on that instances unique ID.
    def get_vm_instance(self, xid) :
        self.logger.log_event(self.logclient, 'GET VM INSTANCE', 'a', ['Instance Id'], xid)
        if self.manager :
            try : 
                inst = self.manager.get_droplet(xid)
                if inst :
                    self.logger.log_event(self.logclient, 'GET VM INSTANCE', 's', ['Instance Id'], xid)
                    return inst
            except Exception, e :
                self.logger.log_event(self.logclient, "GET VM INSTANCE", 'e', ['Instance Id', 'e.what()'], (xid, str(e)))
                return None

        self.logger.log_event(self.logclient, 'GET VM INSTANCE', 'f', ['Instance Id'], xid)
        return None

    # @info - gets the default boot images from the IaaS providers. This includes the special apps like gitlab tht
    #         can be spawned on preexisting images
    def get_boot_images(self) :
        self.logger.log_event(self.logclient, 'GET BOOT IMAGES', 'a')
        if self.manager :
            try : 
                imgs = self.manager.get_images()
                imgs = [self.format_boot_image(img) for img in imgs]
                self.logger.log_event(self.logclient, 'GET BOOT IMAGES', 's', ['#Images'], str(len(imgs)) )
                return imgs
            except Exception, e :
                self.logger.log_event(self.logclient, "GET BOOT INSTANCE", 'e', ['e.what()'], (str(e)))
                return None

        else :
            self.logger.log_event(self.logclient, 'GET BOOT IMAGES', 'f', ['self.manager'], 'Null')
            return None

    # @info - gets all of the custom images of VMs that we have made
    #         This is different from above which gets the default available boot images.
    def get_snapshots(self) :
        self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'a')
        if self.manager :
            try :
                imgs = self.manager.get_images(private=True)
                if imgs :
                    self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 's', ['Num Images'], len(imgs))
                    return [self.format_snapshot(img) for img in imgs]
                else :
                    self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'i', [], "", "Images came back Null")
                    return None
            except Exception, e :
                self.logger.log_event(self.logclient, "GET CUSTOM INSTANCE", 'e', ['e.what()'], (str(e)))
                return None
        else :
            self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'f', ['self.manager'], 'Null')
            return None

    # @info - this gets all the snapshots and looks for the one with the given name
    def get_snapshot_by_name(self, name, inst_name="", desc="") :
        snapshots = self.get_snapshots()
        for ss in snapshots :
            if ss[0][1] == name :
                return self.get_snapshot(ss[1][1], inst_name=inst_name, desc=desc)
        return None

    # @info - takes the id of a snapshot and grabs it from IaaS providers API
    def get_snapshot(self, xid, inst_name="", desc="") :
        self.logger.log_event(self.logclient, 'GET CUSTOM IMAGE', 'a', ['Snapshot ID'], str(xid))
        if self.manager :
            try :
                img = self.manager.get_image(image_id=xid)
                if img :
                    self.logger.log_event(self.logclient, 'GET CUSTOM IMAGE', 's', ['Image Name'], img.name)
                    return self.format_snapshot(img, inst_name, desc)
                else :
                    self.logger.log_event(self.logclient, 'GET CUSTOM IMAGE', 'f', [], "", "Image ID not Found")
                    return None
            except Exception, e :
                self.logger.log_event(self.logclient, "GET CUSTOM IMAGE", 'e', ['e.what()'], (str(e)))
                return None
        else :
            self.logger.log_event(self.logclient, 'GET CUSTOM IMAGE', 'f', ['self.manager'], 'Null')
            return None

    # @info - create a new vm instance, right now only works through digital ocean. Wouldn't be hard to integrate
    #          other IaaS APIs though.
    def create_vm_instance(self, vmargs, sshkeys=[]) :
        try :
            droplet = digitalocean.Droplet(token=self.tok,
                                           name=vmargs['name'],
                                           region=vmargs['region'],
                                           image=vmargs['image'],
                                           ssh_keys=sshkeys,
                                           size_slug=vmargs['class'],
                                           backups=False)
            droplet.create()
            return droplet
        except Exception, e :
            self.logger.log_event(self.logclient, "CREATE VM INSTANCE", 'e', ['e.what()'], (str(e)))
            return None

    # @info - destroy the vm instance tagged with the given ID. Will attempt to destroy it and return true
    #          if it succeeds. 
    def destroy_vm_instance(self, xid) :
        self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'a', ['Instance ID'], (xid)) 
        droplet = self.get_vm_instance(xid)
        try :
            if droplet :
                if droplet.destroy() :
                    return self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 's', ['Instance ID'], (xid)) 
                else :
                    return self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'f', ['Instance ID'], (xid), 
                                                 "droplet.destroy() Failed") 
        except Exception, e :
            self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'e', ['e.what()'], (str(e)))
            return False
        return self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'f', ['Instance ID'], (xid), "Droplet Not Found") 
                
    # @info - get the status of the vm like 'starting', or 'active'
    def get_vm_status(self, xid) :
        inst = self.get_vm_instance(xid)
        if inst :
            status = inst.status
            self.logger.log_event(self.logclient, "GET VM STATUS", 's', ['Instance ID', 'Status'], (xid, status)) 
            return status
        self.logger.log_event(self.logclient, "GET VM STATUS", 'f', ['Instance ID'], (xid), "Instance Came Back NULL") 
        return None
        

    # @info - takes the id of an instance an images its disk, creating a bootable snapshot of the 
    #         instance at the time it was taken. Note that images can only be taken when the instance
    #         is shut down, so if the instance isn't shut down then this function will not work.
    #         returns the action object for the shutdown
    def create_vm_snapshot(self, xid, snap_name, power_off=True) :
        inst = self.get_vm_instance(xid)
        if not inst :
            self.logger.log_event(self.logclient, "CREATE VM SNAPSHOT", 'f', ['Instance ID'], xid, 
                                  "Instance Doesn't Exist (get_vm_instance())")
            return None
        try :
            snap_action = inst.take_snapshot(snap_name, return_dict=False, power_off=True)

            self.logger.log_event(self.logclient, "CREATE VM SNAPSHOT", 's', ['Instance ID', 'Status'], 
                                  (xid, inst.status), "Instance Must Be Powered Off.")
            return snap_action
        except Exception, e :
            self.logger.log_event(self.logclient, "CREATE VM SNAPSHOT", 'e', ['e.what()'], (str(e)))
            return None

    # @info - takes the id of an existing vm snapshot and destroy it. Be careful, snapshot is 
    #         non recoverable after deletion. Returns t/f depending on the success of deletion.
    def delete_vm_snapshot(self, xid) :
        self.logger.log_event(self.logclient, "DELETE VM SNAPSHOT", 'a', ['Snapshot ID'], str(xid))
        snap = self.get_snapshot(xid)
        if not snap :
            return self.logger.log_event(self.logclient, "DELETE VM SNAPSHOT", 'f', ['Snapshot ID'], str(xid), "Snapshot Not Found on IaaS Servers.")

        try :
            ret = snap.destroy()
            return self.logger.log_event(self.logclient, "DELETE VM SNAPSHOT", 's' if ret else 'f', ['Snapshot ID'], str(xid))
        except Exception, e :
            self.logger.log_event(self.logclient, "DELETE VM SNAPSHOT", 'e', ['e.what()'], (str(e)))
            return False

    # @info - takes the id of an existing instance and a snapshot id and attempts to rebuild the instance given by
    #         the id with the snapshot given by the snapshot id. 
    #         returns a 2-tuple (droplet, action)
    def rebuild_vm_snapshot(self, droplet_id, snapshot_id) :
        self.logger.log_event(self.logclient, "REBUILD VM SNAPSHOT", 'a', ['Droplet ID', 'Snapshot ID'],
                              (str(droplet_id), str(snapshot_id)))
        droplet = self.get_vm_instance(droplet_id)

        if not droplet :
            self.logger.log_event(self.logclient, "REBUILD VM SNAPSHOT", 'f', ['Droplet ID', 'Snapshot ID'],
                                  (str(droplet_id), str(snapshot_id)))
            return None
        try :
            action = droplet.rebuild(image_id=snapshot_id, return_dict=False)
            self.logger.log_event(self.logclient, "REBUILD VM SNAPSHOT", 's', ['Droplet ID', 'Snapshot ID'],
                                  (str(droplet_id), str(snapshot_id)), "Rebuild Sequence Initiated")
            return (droplet, action)
        except Exception, e :
            self.logger.log_event(self.logclient, "REBUILD DELETE VM SNAPSHOT", 'e', ['e.what()'], (str(e)))
            return None

    # @info - used to resize a currently existing instance
    def resize_vm_instance(self, inst_id, new_size) :
        pass


    # @info - used to power off the instance with id inst_id. Used when taking a snapshot
    def shutdown_vm_instance(self, inst_id) :
        inst = self.get_vm_instance(inst_id)
        if inst :
            try :
                status = inst.status
                if status not in  ["active", "new"] :
                    return self.logger.log_event(self.logclient, "SHUTDOWN VM INST", 'f',
                                                 ['Instance ID', 'Status'], (inst_id, status),
                                                 "Cannot be Shutdown, Instance Not Active")
                ret = inst.shutdown()
                self.logger.log_event(self.logclient, "SHUTDOWN VM INST", 's', ['Instance ID'], (inst_id), "Instance shutdown Initiated") 
                return ret
            except Exception, e :
                self.logger.log_event(self.logclient, "SHUTDOWN VM INST", 'e', ['e.what()'], (str(e)))
                return None
        self.logger.log_event(self.logclient, "SHUTDOWN VM INST", 'f', ['Instance ID'], (inst_id), "Instance Came Back NULL") 
        return None

    # @info - more aggressive way of shutting down an instance 
    def poweroff_vm_instance(self, inst_id) :
        inst = self.get_vm_instance(inst_id)
        if inst :
            try :
                status = inst.status
                if status not in  ["active", "new"] :
                    return self.logger.log_event(self.logclient, "POWEROFF VM INST", 'f',
                                                 ['Instance ID', 'Status'], (inst_id, status),
                                                 "Cannot be Shutdown, Instance Not Active")
                ret = inst.power_off()
                self.logger.log_event(self.logclient, "POWEROFF VM INST", 's', ['Instance ID'], (inst_id), "Instance Power Off Initiated") 
                return ret
            except Exception, e :
                self.logger.log_event(self.logclient, "POWEROFF VM INST", 'e', ['e.what()'], (str(e)))
                return None
        self.logger.log_event(self.logclient, "POWEROFF VM INST", 'f', ['Instance ID'], (inst_id), "Instance Came Back NULL") 
        return None

    # @info - used to power back on an instance with id inst_id after being shutdown
    def poweron_vm_instance(self, inst_id) :
        inst = self.get_vm_instance(inst_id)
        if inst :
            try :
                status = inst.status
                if status != "off" :
                    return self.logger.log_event(self.logclient, "Power On VM INST", 'f',
                                                 ['Instance ID', 'Status'], (inst_id, status),
                                                 "Cannot be Shutdown, Instance Not Shut Down")
                ret = inst.power_on()
                return ret
            except Exception, e :
                self.logger.log_event(self.logclient, "POWEROFF VM INST", 'e', ['e.what()'], (str(e)))
                return None
        self.logger.log_event(self.logclient, "POWER ON VM INST", 'f', ['Instance ID'], (inst_id), "Instance Came Back NULL") 
        return None


    # @info - waits form a vm to go into the given state. States can be 'new', 'active', 'off'
    #         time_left is how much time you would wait max for the state change
    def wait_for_state(self, inst_id, states, time_left) :
        if not isinstance(states, list) :
            states = [states]

        sleep_amount = 10
        cur_state = self.get_vm_status(inst_id) 

        self.logger.log_event(self.logclient, "WAIT FOR VM STATE", 'a', ['Current State', 'Desired State', 'Time to Wait'], 
                                  (cur_state, str(states), str(time_left)+'sec'))

        while cur_state not in states and time_left > 0:
            time.sleep(sleep_amount)
            self.logger.log_event(self.logclient, "WAIT FOR VM STATE", 'i', ['Current State', 'Desired State', 'Time Left'], 
                                  (cur_state, str(states), str(time_left)+'sec'), "Waiting for VM to change state")
            time_left -= sleep_amount
            cur_state = self.get_vm_status(inst_id) 

        if time_left <= 0 :
            return self.logger.log_event(self.logclient, "WAIT FOR VM STATE", 'f', ['Final State', 'Desired State', 'Time Waited (s)'],
                                         (cur_state, str(states), str(time_left)), "Timed out Waiting for State Change")
        else :
            return self.logger.log_event(self.logclient, "WAIT FOR VM STATE", 's', ['Final State', 'Desired State', 'Time Waited (s)'],
                                         (cur_state, str(states), str(time_left)) )


    # @info - retrive all of the valid ssh keys from the IaaS providers
    def get_ssh_keys(self) :
        if self.manager :
            try :
                sshkeys = self.manager.get_all_sshkeys()
                if sshkeys :
                    self.logger.log_event(self.logclient, "GET SSH KEYS", 's', ['Num Keys'], (str(len(sshkeys))))
                    return sshkeys
            except Exception, e :
                self.logger.log_event(self.logclient, "GET SSH KEYS", 'e', ['e.what()'], str(e))
                return None
        self.logger.log_event(self.logclient, "GET SSH KEYS", 'f', [], "")
        return None

    # @info - retrive a single valid ssh key from the IaaS providers by key id
    def get_ssh_key(self, xid) :
        if self.manager :
            sshkey = self.manager.get_ssh_key(xid)
            try :
                if sshkey :
                    self.logger.log_event(self.logclient, "GET SSH KEY", 's', ['Keys ID'], (str(sshkey.id)))
                    return  sshkey
            except Exception, e :
                self.logger.log_event(self.logclient, "GET SSH KEY", 'e', ['e.what()'], str(e))
                return None
        self.logger.log_event(self.logclient, "GET SSH KEY", 'f', [], "")
        return None

    # @info - takes a given ssh key and adds it to the digital ocean account. Key must contain a name
    #         public-key and fingerprint as a dictionary {'name' : name, 'public_key' : pkey, 'fingerprint' : fp}
    def add_ssh_key(self, key) :
        self.logger.log_event(self.logclient, "ADD SSH KEY", 'a', ['Key Name', 'Key Fingerprint'], (key['name'], key['fingerprint']))
        try :
            newkey = digitalocean.SSHKey(token=self.tok,
                                         name = key['name'],
                                         public_key = key['public_key'])
            newkey.create()
            self.logger.log_event(self.logclient, "ADD SSH KEY", 'f' if not newkey else 's',
                                  ['Key Name', 'Key Fingerprint'], (key['name'], key['fingerprint']))
            return newkey
        except Exception, e :
            self.logger.log_event(self.logclient, "ADD SSH KEY", 'e', ['e.what()'], str(e))
            return None

        

    # @info - takes a list of vm instances and runs them through the instance formatter
    def format_do_instances(self, instances, creator) :
        return [self.format_do_instance(instance, creator) for instance in instances]

    # @info - formats a single instant (and it's creator) into a list of tupled needed 
    #         for insertion into the Instances table in our database. Since the given
    #         instance dictionary contains info about ssh keys and snapshots, we store
    #         those and return them too in a 3-tuple.
    def format_do_instance(self, instance, creator ) :
        dbargs = [ 
                 ("id", instance.id),
                 ("name", instance.name),
                 ("image", instance.image['id']),
                 ("ip", instance.ip_address),
                 ("ipv6", instance.ip_v6_address),
                 ("class", instance.size_slug),
                 ("disk", instance.disk),
                 ("region", instance.region['slug']),
                 ("status", instance.status),
                 ("creator", creator),
                 ("created_at", self.format_time_str(str(instance.created_at))),
                 ("provider", "DO"),
             ]
        imgargs = [("snapshot_ids", instance.snapshot_ids),
                  ("backup_ids", instance.backup_ids)] 

        keyargs = [("sshkeys", instance.ssh_keys)]

        return (dbargs, imgargs, keyargs)

    # @info - formats an ssh key so it can be inserted into the database
    def format_ssh_key(self, key, user) :
        return [ 
                 ("id", key.id),
                 ("user", user),
                 ("name", key.name),
                 ("pubkey", key.public_key),
                 ("fingerprint", key.fingerprint),
                ]

    # @info - formats a snapshot dictionary so it can be stored in the database
    def format_snapshot(self, image, inst_name="", desc="") :
        return [ 
                ("name", image.name),
                ("id", image.id),
                ("instancename", inst_name),
                ("created_at", self.format_time_str(str(image.created_at))),
                ("provider", "DO"),
                ("description", desc),
                ("region", image.regions[0]),
                ]

    def format_boot_image(self, image) :
        return [
                ("id", image.id),
                ("name", image.name),
                ("slug", image.slug),
                ("disto", image.distribution)
                ]

    # @info formts a ISO YY:MM:DDTHH:MM:SSZ time string properly for the SQL Datetime type
    def format_time_str(self, timestr) :
        dt = datetime
        ret = dt.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ")
        return ret.strftime('%Y-%m-%d %H:%M:%S')

