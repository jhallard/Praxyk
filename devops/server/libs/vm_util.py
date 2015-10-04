#!/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import digitalocean
import datetime
import socket

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
    def get_vm_instance(self, id) :
        self.logger.log_event(self.logclient, 'GET VM INSTANCE', 'a', ['Instance Id'], id)
        if self.manager :
            try : 
                inst = self.manager.get_droplet(id)
                if inst :
                    self.logger.log_event(self.logclient, 'GET VM INSTANCE', 's', ['Instance Id'], id)
                    return inst
            except Exception, e :
                self.logger.log_event(self.logclient, "GET VM INSTANCE", 'e', ['Instance Id', 'e.what()'], (id, str(e)))
                return None

        self.logger.log_event(self.logclient, 'GET VM INSTANCE', 'f', ['Instance Id'], id)
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
					self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'f', [], "", "Images came back Null")
					return None
			except Exception, e :
				self.logger.log_event(self.logclient, "GET CUSTOM INSTANCE", 'e', ['e.what()'], (str(e)))
				return None
        else :
            self.logger.log_event(self.logclient, 'GET CUSTOM IMAGES', 'f', ['self.manager'], 'Null')
            return None

    # @info - create a new vm instance, right now only works through digital ocean. Wouldn't be hard to integrate
    #	      other IaaS APIs though.
    def create_vm_instance(self, vmargs) :
        droplet = digitalocean.Droplet(token=self.tok,
                                       name=vmargs['name'],
                                       region=vmargs['region'],
                                       image=vmargs['image'],
                                       size_slug=vmargs['class'],
                                       backups=False)
        droplet.create()
        return droplet

	# @info - destroy the vm instance tagged with the given ID. Will attempt to destroy it and return true
	#		  if it succeeds. 
    def destroy_vm_instance(self, xid) :
     	self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'a', ['Instance ID'], (xid)) 
    	droplet = self.get_vm_instance(xid)
    	if droplet :
    		if droplet.destroy() :
    			return self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 's', ['Instance ID'], (xid)) 
    		else :
    			return self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'f', ['Instance ID'], (xid), 
    									     "droplet.destroy() Failed") 
    	return self.logger.log_event(self.logclient, "DESTROY VM INSTANCE", 'f', ['Instance ID'], (xid), "Droplet Not Found") 
				
    # @info - get the status of the vm like 'starting', or 'active'
    def get_vm_status(self, id) :
        inst = self.get_vm_instance(id)
        if inst :
            status = inst.status
            self.logger.log_event(self.logclient, "GET VM STATUS", 's', ['Instance ID', 'Status'], (id, status)) 
            return status
        self.logger.log_event(self.logclient, "GET VM STATUS", 'f', ['Instance ID'], (id), "Instance Came Back NULL") 
        return None
    	

    # @info - takes the id of a *SHUT DOWN* instance and takes a snapshot of it. VMs cannot be imaged
    #         while running on DO. They can be backed up though.
    def create_vm_snapshot(self, xid) :
        # @TODO - create snapshot of running instance
        pass


    # @info - takes a list of vm instances and runs them through the instance formatter
    def format_do_instances(self, instances) :
        return [self.format_do_instance(instance) for instance in instances]

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
    def format_ssh_key(self, key) :
        return [ 
                 ("id", key.id),
                 ("name", key.name),
                 ("pubkey", key.pubkey),
                 ("fingerprint", key.fingerprint),
                ]

    # @info - formats a snapshot dictionary so it can be stored in the database
    def format_snapshot(self, image, inst_name="") :
        return [ 
                ("name", image.name),
                ("id", image.id),
                ("instancename", inst_name),
                ("created_at", self.format_time_str(str(image.created_at))),
                ("provider", "DO"),
                ("description", ""),
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

