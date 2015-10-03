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

        self.logtail(ret)
        return ret

    def test_login(self) :
        desc = "Testing login through Digital Ocean API"
        return self.maintest(sys._getframe().f_code.co_name, desc, 
                             self.vmutil.login())
