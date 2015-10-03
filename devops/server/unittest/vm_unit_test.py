#!/bin/env python

# @info - Unit testing suite for the vmUtil class which handles all interaction
#         for our team with the various IaaS providers (DO, GCE, AWS). We'll
#         test create and destroy some VMs.
from unit_test import *
from vm_util import *


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

