#!/bin/env python

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
        self.head_data=[] # Add info to log at top of test log file here
        self.tail_data=[] # ^^ bottom of test file here

        UnitTest.__init__(self, testargs)
        self.vmutil = vmUtil(vmargs)

    def run(self) :
        ret = True
        ret = ret and self.test_login()
        ret = ret and self.test_get_boot_images()
        ret = ret and self.test_get_custom_images()
        ret = ret and self.test_get_running_instances()
        ret = ret and self.test_formatting_instances()
        ret = ret and self.test_create_destroy_instance()

        self.logtail(ret)
        return ret

    def test_login(self) :
        desc = "Testing login through IaaS API"
        return self.maintest(sys._getframe().f_code.co_name, desc, 
                             self.vmutil.login())

    def test_get_boot_images(self) :
        desc = "Get the Available Boot-Images from IaaS Provider"
        self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login())

        return self.maintest(sys._getframe().f_code.co_name, desc,
                             self.vmutil.get_boot_images() != None)


    def test_get_custom_images(self) :
        desc = "Get the Available Boot-Images from IaaS provider"
        self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login())

        return self.maintest(sys._getframe().f_code.co_name, desc,
                             self.vmutil.get_custom_images() != None)


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

        formatted = self.vmutil.format_do_instances(instances)
        self.logger.log_event(self.logclient,"FORMATTING INSTACES", 'i', ['Instances Grabbed'], str(formatted))
        return self.maintest(sys._getframe().f_code.co_name, desc, formatted != None)

    def test_create_destroy_instance(self) :
	""" This test grabs will attempt to create and destroy an instance on digital ocean. It takes about a minute to spin
            up an instance so it will actually wait for the status of instance to go to active before attempting to delete it"""
        desc = "Create and Delete a single VM Instance"

        vmargs = { 'name' : 'TEST-INST-ALPH',
                   'region' : 'sfo1',
                   'image'  : 'ubuntu-14-04-x64',
                   'class'  : '1gb'
                   }

        if not self.subtest(sys._getframe().f_code.co_name, "Logging In with IaaS Provider", self.vmutil.login()) :
            return False

        droplet = self.vmutil.create_vm_instance(vmargs)
        self.subtest(sys._getframe().f_code.co_name, "Droplet Creation Started", droplet != None)

        time_left = 180 # 2 minutes
        sleep_amount = 10
        while self.vmutil.get_vm_status(droplet.id) != 'active' and time_left > 0:
            time.sleep(sleep_amount)
            self.logger.log_event(self.logclient, "TEST INFO", 'i', ['Time Left'], str(time_left), "Waiting for VM to go Active..")
            time_left -= sleep_amount

        if time_left <= 0 :
            self.maintest(sys._getframe().f_code.co_name, "Timed out Waiting for Active State", False)
            return False

        self.maintest(sys._getframe().f_code.co_name, "New Instance Created and Active", True)

        res = self.vmutil.destroy_vm_instance(droplet.id)
        
        return self.maintest(sys._getframe().f_code.co_name, desc, res)





