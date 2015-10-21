#!/bin/env python
import _fix_path_
import sys
import datetime

class UnitTest :

    def maintest(self,name, desc, f) :
        return self.logger.log_event(self.logclient, 'UNIT TEST', ("s" if f else "f"),
                                    ['Test Name', 'Description'],
                                    (str(name), desc) )

    # this is used for asserting actions are true that don't constiitute the main prupose of 
    # a test, but still needs to be logged and verified. Ex - a test that tries to update items
    # in a database might need to login to the DB first, they would pass the result of the login
    # attempt to this function, but the result of the updates to the maintest() function
    def subtest(self,name, desc, f) :
        return self.logger.log_event(self.logclient, 'SUB-TEST', ("s" if f else "f"),
                                    ['Test Name', 'Description'],
                                    (str(name), desc) )

    def logteststart(self, name, info="") :
        return self.logger.log_event(self.logclient, 'UNIT TEST', 'a', ['Test Name', 'Info'], (name, info))

    def loginfo(self, name, info) :
        return self.logger.log_event(self.logclient, 'TEST-INFO', "i", ['Message'], str(info))

    def loghead(self) :
        title = self.title + ' UNIT TEST START '
        exchar = '-'
        logstr =  '\n' + 30*exchar + title + 30*exchar + '\n'
        logstr += '''Start Time : ''' +  str(datetime.datetime.now()).split(' ')[1] + '\n'
        for data in self.head_data :
            logstr += 3*exchar+' [%s] \n' % data
        logstr +=  30*exchar + len(title)*exchar + 30*exchar + '\n'
        self.logger.logblock(self.logclient, logstr)

    def logtail(self, result) :
        title =  self.title + ' UNIT TEST FINISH '
        exchar = '-'
        logstr =  '\n' + 30*exchar + title + 30*exchar + '\n'
        logstr += 'End Time   : ' +  str(datetime.datetime.now()).split(' ')[1] + '\n'
        logstr += 'Result     : ' + str(result) + '\n'
        for data in self.tail_data :
            logstr += 3*exchar+' [%s] \n' % data
        logstr +=  30*exchar  + len(title)*exchar + 30*exchar + '\n'
        self.logger.logblock(self.logclient, logstr)

    def __init__(self, testargs) : #logftest, testtbl, schema) :
        self.passed = False
        self.head_data
        self.tail_data
        self.title
        self.logclient = testargs['logclient']
        self.logger = testargs['logutil']
        self.loghead()
