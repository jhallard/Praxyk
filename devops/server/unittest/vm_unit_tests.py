#!/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT


# @info - Unit testing suite for the vmUtil class which handles all interaction
#         for our team with the various IaaS providers (DO, GCE, AWS). We'll
#         test create and destroy some VMs.
from unit_test import *
from vm_util import *

import time


class vmUnitTest(UnitTest) :

    def __init__(self, vmargs, testargs) :
        self.title = 'Virtual-Machine Util'
        self.logger = testargs['logutil']
        self.logclient = testargs['logclient']
        self.flags = [flag for flag in str(testargs['flags'])] # turns a string 'abcdef' --> ['a', 'b', 'c', .. 'f'] containing test flags
        self.head_data=[] # Add info to log at top of test log file here
        self.tail_data=[] # ^^ bottom of test file here

        UnitTest.__init__(self, testargs)
        self.vmutil = vmUtil(vmargs)

        self.snapshot_id1 = 0  # used by our snapshot tests, need to store id of created
                               # ones to delete in further tests
        self.instance_id1 = 0 # vm built from scratch in create_instance()
        self.sshkey = vmargs['sshkey']

    def run(self) :
        ret = True
        ret = ret and self.test_login()

        if 'a' in self.flags : 
            # create and destroy a single instance from scratch
            ret = ret and self.test_create_instance()
            ret = ret and self.test_destroy_instance()

        if 'b' in self.flags :
            # create and destroy a new instance from a snapshot
            ret = ret and self.test_build_vm_snapshot()
            ret = ret and self.test_destroy_instance()

        if 'c' in self.flags :
            # create an instance, poweroff, take a snapshot, delete the snapshot, delete the instance
            ret = ret and self.test_create_instance()
            ret = ret and self.test_poweroff_instance()
            ret = ret and self.test_create_snapshot()
            ret = ret and self.test_poweron_instance()
            ret = ret and self.test_delete_snapshot()
            ret = ret and self.test_destroy_instance()
    
        if 'd' in self.flags :
            # standard health check
            ret = ret and self.test_get_sshkeys()
            ret = ret and self.test_get_boot_images()
            ret = ret and self.test_get_snapshots()
            ret = ret and self.test_get_running_instances()
            ret = ret and self.test_formatting_instances()
        
        if 'e' in self.flags :
            # create an instance, rebuild it from an image, destroy the instance
            ret = ret and self.test_create_instance()
            ret = ret and self.test_rebuild_vm_snapshot()
            ret = ret and self.test_destroy_instance()

        if 'f' in self.flags :
            ret = ret and self.test_create_snapshot()
            ret = ret and self.test_delete_snapshot()

        if 'g' in self.flags :
            ret = ret and self.test_add_sshkey()

        self.logtail(ret)
        return ret

        # ret = ret and self.test_get_boot_images()
        # ret = ret and self.test_get_snapshots()
        # ret = ret and self.test_get_running_instances()
        # ret = ret and self.test_formatting_instances()
        # ret = ret and self.test_create_instance()
        # ret = ret and self.test_poweroff_instance()
        # ret = ret and self.test_create_snapshot()
        # ret = ret and self.test_rebuild_vm_snapshot()
        # ret = ret and self.test_build_vm_snapshot()
        # ret = ret and self.test_poweron_instance()
        # ret = ret and self.test_delete_snapshot()
        # ret = ret and self.test_destroy_instance()

    def test_login(self) :
        desc = "Testing login through IaaS API"
        return self.maintest(sys._getframe().f_code.co_name, desc, 
                             self.vmutil.login())

    def test_get_boot_images(self) :
        desc = "Get the Available Boot-Images from IaaS Provider"
        self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login())
        res = self.vmutil.get_boot_images() 
        return self.maintest(sys._getframe().f_code.co_name, desc, res != None)


    def test_get_snapshots(self) :
        desc = "Get the Available Boot-Images from IaaS provider"
        self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login())

        res = self.vmutil.get_snapshots() 
        # if res :
            # self.logger.log(self.logclient, str([str([str(k) + str(v) for (k,v) in imgs]) for imgs in res]) )
            # self.logger.log(self.logclient, str([str(k) for k in res]) )

        return self.maintest(sys._getframe().f_code.co_name, desc, True) # if res is none it just means we
                                                                         # have no images currently

    def test_get_sshkeys(self) :
        desc = "Get the Available SSH Keys in Bulk then One By One"
        self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login())
        keys = self.vmutil.get_ssh_keys() 
        res = self.subtest(sys._getframe().f_code.co_name, "Get All SSH Keys", keys != None)

        for key in keys :
            key_2 = self.vmutil.get_ssh_key(key.id)
            res = res and self.subtest(sys._getframe().f_code.co_name, "Get single SSH Key", key_2 != None)

        return self.maintest(sys._getframe().f_code.co_name, desc, res)

    def test_get_running_instances(self) :
        desc = "Get Any VMs Currently Running in the Cloud."
        self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login())
        
        return self.maintest(sys._getframe().f_code.co_name, desc,
                             self.vmutil.get_vm_instances() != None)

    def test_formatting_instances(self) :
        """ This test grabs all of the running instances like above, but instead of ending then it instead
            forwards the instances to the format_instances function to ensure that they can be formatted for
            the db correctly. """
        desc = "Get any VMs Running and Test the InstanceFormat Function by Running them through it."
        instances = []

        if not self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login()) :
            return False

        instances = self.vmutil.get_vm_instances()
        if not self.subtest(sys._getframe().f_code.co_name, "Getting All VMs from IaaS providers.", instances != None) :
            return False

        formatted = self.vmutil.format_do_instances(instances, "TEST-USER")
        # self.logger.log_event(self.logclient,"FORMATTING INSTACES", 'i', ['Instances Grabbed'], str(formatted))
        return self.maintest(sys._getframe().f_code.co_name, desc, formatted != None)

    def test_create_instance(self) :
	""" This test grabs will attempt to create an instance on digital ocean. It takes about a minute to spin
            up an instance so it will actually wait for the status of instance to go to active before returning True"""
        desc = "Create a single VM Instance"

        vmargs = { 'name' : 'TEST-INST-ALPH',
                   'region' : 'sfo1',
                   'image'  : 'ubuntu-14-04-x64',
                   'class'  : '1gb'
                   }

        if not self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login()) :
            return False

        droplet = self.vmutil.create_vm_instance(vmargs)
        self.subtest(sys._getframe().f_code.co_name, "Droplet Creation Started", droplet != None)
        self.instance_id1 = str(droplet.id)

        # wait for the vm to go active
        went_active = self.vmutil.wait_for_state(droplet.id, ['active', 'new'], 180)

        return self.maintest(sys._getframe().f_code.co_name, "New Instance Created and Active", went_active)

    def test_poweroff_instance(self) :
        """ This Test will PowerOff a running instance"""
        desc = "Poweroff a single VM Instance"

        if not self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login()) :
            return False

        is_up = self.vmutil.wait_for_state(self.instance_id1, 'active', 240)

        res = self.vmutil.poweroff_vm_instance(self.instance_id1)

        went_off = self.vmutil.wait_for_state(self.instance_id1, 'off', 440)

        return self.maintest(sys._getframe().f_code.co_name, "New Instance Powered Off", went_off == True)

    def test_poweron_instance(self) :
        """ This Test will Power On a running instance"""
        desc = "Power On a single VM Instance"

        if not self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login()) :
            return False

        is_down = self.vmutil.wait_for_state(self.instance_id1, 'off', 180)

        res = self.vmutil.poweron_vm_instance(self.instance_id1)

        self.subtest(sys._getframe().f_code.co_name, "Droplet Power On Started", res != None)
        self.logger.log_event(self.logclient, "TEST POWERON INSTANCE", 'i', ['API Returned From Power ON'], str(res))
        
        went_on = self.vmutil.wait_for_state(self.instance_id1, ['active', 'new'], 180)

        return self.maintest(sys._getframe().f_code.co_name, "New Instance Powered On and Active", went_on == True)

    def test_create_snapshot(self) :
	""" This test will attempt to make a snapshot of a vm instance that was just created"""
        desc = "Take a Snapshot of a single VM Instance"
        
        if not self.instance_id1 :
            self.instance_id1 = self.vmutil.get_vm_instances()[0].id #the first instance
            
        snap = self.vmutil.create_vm_snapshot(self.instance_id1, 'TEST-SNPSHT')
        snap.wait(5)

        self.logger.log_event(self.logclient, "TEST-INFO", 'i', ['Snapshot Details'], str(snap))
        return self.maintest(sys._getframe().f_code.co_name, desc, snap != None)

    # takes a current VM and rebuilds it with a snapshot
    def test_rebuild_vm_snapshot(self) :
        """ This test will attempt to rebuild an existing VM from a recently taken snapshot. It will confirm the
            new VM is created and active before concluding."""
        desc = "Rebuilds an Existing VM instance from a snapshot"
        snapshot = self.vmutil.get_snapshots()[0]
        self.snapshot_id1 = snapshot[1][1]

        is_up = self.vmutil.wait_for_state(self.instance_id1, 'active', 340)

        (droplet, action) = self.vmutil.rebuild_vm_snapshot(self.instance_id1, self.snapshot_id1)
        self.logger.log_event(self.logclient, "TEST-INFO", 'i', ['New Droplet Details'], str(droplet))

        went_active = self.vmutil.wait_for_state(droplet.id, ['active', 'new'], 180)
        action.wait(5)
        return self.maintest(sys._getframe().f_code.co_name, "New Instance Rebuilt and Active", went_active)

    # builds a new VM from scratch from a snapshot
    def test_build_vm_snapshot(self) :
        """ This test will attempt to make a new VM from a recently taken snapshot. It will confirm the
            new VM is created and active before concluding."""
        desc = "Builds a new VM instance from a snapshot"
        snapshot = self.vmutil.get_snapshots()[0]

        vmargs = { 'name' : 'TEST-INST-BETA',
                   'region' : 'sfo1',
                   'image'  : snapshot[1][1],
                   'class'  : '1gb'
                   }

        droplet = self.vmutil.create_vm_instance(vmargs)
        self.logger.log_event(self.logclient, "TEST-INFO", 'i', ['New Droplet Details'], str(droplet))
        self.subtest(sys._getframe().f_code.co_name, "Droplet Creation Started", droplet != None)
        self.instance_id1 = str(droplet.id)

        # wait for the vm to go active
        went_active = self.vmutil.wait_for_state(droplet.id, ['active', 'new'], 180)

        return self.maintest(sys._getframe().f_code.co_name, "New Instance Rebuilt and Active", went_active)

    def test_delete_snapshot(self) :
	""" This test will attempt to delete a snapshot that was just created."""
        desc = "Delete a  Snapshot of a single VM Instance"

        if not self.snapshot_id1 :
            snapshot = self.vmutil.get_snapshots()[0]
            self.snapshot_id1 = snapshot[1][1]
        snap = self.vmutil.delete_vm_snapshot(self.snapshot_id1)
        self.logger.log_event(self.logclient, "TEST-INFO", 'i', ['Snapshot Details'], str(snap))
        return self.maintest(sys._getframe().f_code.co_name, desc, snap != None)


    def test_destroy_instance(self) :
	""" This test grabs will attempt to destroy an instance on digital ocean that was created by the test_create_instance test. """
        desc = "Destroy a single VM Instance"

        vmargs = { 'name' : 'TEST-INST-ALPH',
                   'region' : 'sfo1',
                   'image'  : 'ubuntu-14-04-x64',
                   'class'  : '1gb'
                   }

        is_active = self.vmutil.wait_for_state(self.instance_id1, ['active'], 300)
        if not is_active :
            return self.maintest(sys._getframe().f_code.co_name, "Instance Never Went Active to Destroy", False)
        res = self.vmutil.destroy_vm_instance(self.instance_id1)
        return self.maintest(sys._getframe().f_code.co_name, desc, res)


    def test_add_sshkey(self) :
        """This test takes a given ssh key (public key, fingerprint, name assigned to it) and puts it onto the digital ocean account"""
        desc = "Add a new SSH Key to the IaaS account"

        keyargs = {'name' : self.sshkey['name'],
                   'public_key' : self.sshkey['public_key'],
                   'fingerprint' : self.sshkey['fingerprint'] }

        key = self.vmutil.add_ssh_key(keyargs)

        return self.maintest(sys._getframe().f_code.co_name, desc, key is not None)





