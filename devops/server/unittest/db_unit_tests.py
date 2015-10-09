#!/usr/bin/python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import _fix_path_
from db_util import *
from unit_test import *

import sys

class dbUnitTest(UnitTest) :

    def __init__(self, dbargs, testargs) : #logftest, testtbl, schema) :
        self.title = 'dbUtil'
        self.schema = testargs['schema']
        self.dbname = self.schema['dbname']
        self.table = testargs['testtable']
        self.head_data=['Schema    : %s' % self.schema['file'],
                        'Test Table: %s' % self.table]
        self.tail_data=[]

        UnitTest.__init__(self, testargs)

        self.dbutil = dbUtil(dbargs)
        self.db = self.dbutil.login()

        # these are the various databases we use temporarily for the test, the first one
        # corresponds to our schema, which is our main test one. the others are used just to
        # ensure we can create and drop databases multiple times.
        self.dbnames = [self.dbname, 'copy', 'CDATAB2', 'CDATAB3']
        self.clear_test_databases(self.dbnames)

    def clear_test_databases(self, names) :
        for name in names :
            if self.dbutil.database_exists(name) :
                self.logger.log_event(self.logclient, 'INITIALIZATION', 'a',
                                     ['Database Drop'], self.dbname,  '( Already Exists )')
                if self.dbutil.drop_database(name) :
                    self.logger.log_event(self.logclient, 'INITIALIZATION', 's',
                                         ['Database Drop'], self.dbname, 'Continuing Test' )
                else :
                    self.logger.log_event(self.logclient, 'INITIALIZATION', 'f',
                                         ['Database Drop'], self.dbname, 'Ending Test' )
                    sys.exit(1)
        return True


    def clear_table(self, name) :
        cur = self.db.cursor()
        cur.execute('''SHOW TABLES LIKE '%s' ''' % name)
        if cur.fetchall() :
            cur.execute('''DELETE FROM %s'''%name)
            self.db.commit()

    def fill_buffer(self, name) :
        table=name
        self.clear_table(table)
        MAX=100
        alph = ['a','b','c','d']
        pos = [str(x)+str(y)+str(z) for x in alph for y in alph for z in alph]
        dat = [p+str(q) for p in pos for q in alph]
        vals = [[('name', pos[x]), ('data', dat[x])] for x in range(0, len(pos)-1) ]
        passed=True
        for val in vals[:MAX] :
             if not self.dbutil.insert(table, val) :
                 passed=False
        return passed

    def run(self) :
        r = self.build_database()       and \
            self.run_queries()          and \
            self.run_subqueries()       and \
            self.run_table_creates()    and \
            self.run_table_drops()      and \
            self.run_database_creates() and \
            self.run_database_drops()   and \
            self.run_inserts()          and \
            self.run_deletes()          and \
            self.run_updates()
        self.logtail(r)
        return r

    def build_database(self) :
        return (
            self.test_build_db_1()
        )

    def run_queries(self) :
        return (
            self.test_query_1() and
            self.test_query_2() and
            self.test_query_3()
        )

    def run_subqueries(self) :
        return (
            self.test_subquery_1() and
            self.test_subquery_2() #and
            # self.test_subquery_3()
        )

    def run_table_creates(self) :
        return (
            self.test_table_create_1() and
            self.test_table_create_2() and
            self.test_table_create_3()
        )

    def run_table_drops(self) :
        return (
            self.test_table_drop_1() and
            self.test_table_drop_2() and
            self.test_table_drop_3()
        )

    def run_database_creates(self) :
        return (
            self.test_database_create_1() and
            self.test_database_create_2() and
            self.test_database_create_3()
        )

    def run_database_drops(self) :
        return (
            self.test_database_drop_1() and
            self.test_database_drop_2() and
            self.test_database_drop_3() and
            self.test_database_drop_4()
        )

    def run_inserts(self) :
        return (
            self.test_insert_1() and
            self.test_insert_2() and
            self.test_insert_3() and
            self.test_insert_4() and
            self.test_insert_5()
        )

    def run_updates(self) :
        return (
            self.test_update_1() and
            self.test_update_2() and
            self.test_update_3() and
            self.test_update_4()
        )

    def run_deletes(self) :
        return (
            self.test_delete_1() and
            self.test_delete_2() and
            self.test_delete_3() and
            self.test_delete_4()
        )


    def test_build_db_1(self) :
        description= "Building Database : " + self.dbname + " Tables : " + str(self.schema['tables'])
        self.loginfo(sys._getframe().f_code.co_name, description)
        passed = self.subtest(sys._getframe().f_code.co_name, description,
                                 self.dbutil.build_database(self.schema))

        tbls = self.dbutil.query('information_schema.tables', 'TABLE_NAME')
        tbls = [tbl[0] for tbl in tbls]
        for x in self.schema['tables'] :
            if x not in tbls :
                self.subtest(sys._getframe().f_code.co_name, str(x[0]) + ''' Table not found in db''',
                                False)
                passed=False
        self.maintest(sys._getframe().f_code.co_name, "All Tables Created and Validated", passed)
        return passed

    ##### QUERY TESTS #####

    def test_query_1(self) :
        self.clear_table(self.table)
        self.fill_buffer(self.table)
        table=self.table
        rows='*'
        cond='1=1'
        description= table + " Query for (" + rows + ") on (" + cond + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.query(table, rows, cond))

    def test_query_2(self) :
        table=self.table
        rows='name, data'
        cond="name like '%ab%'"
        description= table + " Query for (" + rows + ") on (" + cond + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.query(table, rows, cond))

    def test_query_3(self) :
        table=self.table
        rows='data'
        cond="data like 'aaa%'"
        description= table + " Query for (" + rows + ") on (" + cond + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.query(table, rows, cond))


    ##### SUBQUERY TESTS #####

    def test_subquery_1(self) :
        table=self.table
        rows='name, data'
        cond="data like 'aaa%'"
        subq = self.dbutil.subquery(table, rows, cond)

        description= table + " SubQuery for (" + rows + ") on (" + cond + ")"
        self.maintest(sys._getframe().f_code.co_name, description,
         subq)
        rows='*'
        cond='1=1'
        description= table + " Query for (" + rows + ") on (" + cond + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return subq and self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.query(subq, rows, cond))

    def test_subquery_2(self) :
        table=self.table
        rows='name, data'
        cond="data like 'aaa%'"
        subq = self.dbutil.subquery(table, rows, cond)
        description= table + " SubQuery for (" + rows + ") on (" + cond + ")"
        self.maintest(sys._getframe().f_code.co_name, description,
         subq)
        rows='name'
        cond="name like 'a%'"
        description= table + " Query for (" + rows + ") on (" + cond + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        query = self.dbutil.query(subq, rows, cond)

        return self.maintest(sys._getframe().f_code.co_name, description, len(query)> 0)

    ##### TABLE CREATE TESTS #####

    def test_table_create_1(self) :
        table=self.table
        vals=[['name'], ['data']]
        description="Create Table " + table + ",  Rows (" + self.dbutil.format_keys(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         not self.dbutil.create_table(table, vals))

    def test_table_create_2(self) :
        table='TEMP'
        vals=[['name varchar(200) PRIMARY KEY'], ['data varchar(400)']]
        description="Create Table " + table + ",  Rows (" + self.dbutil.format_keys(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.create_table(table, vals))

    def test_table_create_3(self) :
        table='TEMP2'
        vals=[['name varchar(200) PRIMARY KEY'], ['readme varchar(400)', 'timestamp datetime']]
        description="Create Table " + table + ",  Rows (" + self.dbutil.format_keys(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.create_table(table, vals))


    ##### TABLE DROP TESTS #####

    def test_table_drop_1(self) :
        table='NOT_EXISTS'
        description="Drop Table " + table
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         not self.dbutil.drop_table(table))

    def test_table_drop_2(self) :
        table='TEMP'
        description="Drop Table " + table
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.drop_table(table))

    def test_table_drop_3(self) :
        table='TEMP2'
        description="Drop Table " + table
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.drop_table(table))


    ##### DATABASE CREATE TESTS #####

    def test_database_create_1(self) :
        database=self.dbnames[1]
        description="Create Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.create_database(database))

    def test_database_create_2(self) :
        database=self.dbnames[2]
        description="Create Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.create_database(database))

    def test_database_create_3(self) :
        database=self.dbnames[3]
        description="Create Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.create_database(database))


    ##### DATABASE DROP TESTS #####

    def test_database_drop_1(self) :
        database='NOT_EXISTS_DB'
        description="Drop Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         not self.dbutil.drop_database(database))

    def test_database_drop_2(self) :
        database=self.dbnames[2]
        description="Drop Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.drop_database(database))

    def test_database_drop_3(self) :
        database=self.dbnames[3]
        description="Drop Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.drop_database(database))

    def test_database_drop_4(self) :
        database=self.dbnames[1]
        description="Drop Database " + database
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.drop_database(database))


    ##### INSERT TESTS #####

    def test_insert_1(self) :
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.insert(table, vals))

    def test_insert_2(self) :
        table=self.table
        self.clear_table(table)
        vals1 =[('name','BBB'), ('data', 'lksjdfoijeoiwjeosijdlkfsndclns')]
        vals2 = [('name','CCC'), ('data', '023481098734923')]
        vals3 = [('name','DDD'), ('data', 'sdlkjflskjdlkfjsld3')]
        vals = [vals1, vals2, vals3]
        passed=True
        for val in vals :
            description=table + " Insert for (" + self.dbutil.format_keyvals(val) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
             self.dbutil.insert(table, val)) :
             passed=False
        return passed

    def test_insert_3(self) :
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'lksjdfoijeoiwjeosijdlkfsndclns')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        passed = self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.insert(table, vals))
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return passed and self.maintest(sys._getframe().f_code.co_name, description,
         not self.dbutil.insert(table, vals))

    def test_insert_4(self) :
        description=""
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        passed = self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.insert(table, vals))
        description= table + " Query for (*) on (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return passed and self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.query(table, self.dbutil.format_keys(vals)))

    def test_insert_5(self) :
        table=self.table
        self.clear_table(table)
        vals1 =[('name','BBB'), ('data', 'lksjdfoijeoiwjeosijdlkfsndclns')]
        vals2 = [('name','CCC'), ('data', '023481098734923')]
        vals3 = [('name','DDD'), ('data', 'sdlkjflskjdlkfjsld3')]
        vals = [vals1, vals2, vals3]
        MAX=10
        alph = ['a','b','c','d','e']
        pos = [str(x)+str(y)+str(z) for x in alph for y in alph for z in alph]
        dat = [str(x)+str(y)+str(z)+str(q) for x in alph for y in alph for z in alph for q in alph]
        vals = [[('name', pos[x]), ('data', dat[x])] for x in range(0, len(pos)-1) ]
        passed=True
        for val in vals[:MAX] :
            description=table + " Insert for (" + self.dbutil.format_keyvals(val) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
             self.dbutil.insert(table, val)) :
             passed=False
        return passed


    ##### UPDATE TESTS #####

    def test_update_1(self) :
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        passed = self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.insert(table, vals))
        vals2=[('name','ABAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Update for (" + self.dbutil.format_keyvals(vals2) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return passed and self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.update(table, vals2, self.dbutil.format_keyandvals(vals[0])))

    def test_update_2(self) :
        table=self.table
        self.clear_table(table)
        vals1 =[('name','BBB'), ('data', 'lksjdfoijeoiwjeosijdlkfsndclns')]
        vals2 = [('name','CCC'), ('data', '023481098734923')]
        vals3 = [('name','DDD'), ('data', 'sdlkjflskjdlkfjsld3')]
        vals = [vals1, vals2, vals3]
        passed=True
        for val in vals :
            description=table + " Insert for (" + self.dbutil.format_keyvals(val) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
             self.dbutil.insert(table, val)) :
             passed=False
        for val in vals :
            vals_new = [val[0], ('data',"XXXXXX")]
            description=table + " Update for (" + self.dbutil.format_keyvals(vals_new) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
             self.dbutil.update(table, vals_new, self.dbutil.format_keyandvals(val))) :
             passed=False
        return passed

    def test_update_3(self) :
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        passed = self.maintest(sys._getframe().f_code.co_name, description,
                                 self.dbutil.insert(table, vals))
        vals2=[('name','AAA'), ('data', 'ksl;jsllskdlkjflksj03290293023232232332sjdf')]
        description=table + " Insert or Update for (" + self.dbutil.format_keyvals(vals2) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return passed and self.maintest(sys._getframe().f_code.co_name, description,
                            self.dbutil.insert_or_update(table, vals2, self.dbutil.format_keyandvals(vals[0])))

    def test_update_4(self) :
        table=self.table
        self.clear_table(table)
        alph = ['a','b','c','d','e']
        pos = [str(x)+str(y)+str(z) for x in alph for y in alph for z in alph]
        dat = [str(x)+str(y)+str(z)+str(q) for x in alph for y in alph for z in alph for q in alph]
        vals = [[('name', pos[x]), ('data', dat[x])] for x in range(0, len(pos)-1) ]
        passed=True
        MAX=10
        for val in vals[:MAX] :
            description=table + " Insert for (" + self.dbutil.format_keyvals(val) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
             self.dbutil.insert(table, val)) :
             passed=False
        for val in vals[:MAX] :
            vals_new = [val[0], ('data',"XXXXXX")]
            description=table + " Update for (" + self.dbutil.format_keyvals(vals_new) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
             self.dbutil.update(table, vals_new, self.dbutil.format_keyandvals(val))) :
             passed=False
            if not self.maintest(sys._getframe().f_code.co_name, description,
                                   0 < self.dbutil.query(table, self.dbutil.format_keys(vals_new),
                                                         self.dbutil.format_keyandvals(vals_new))) :
             passed=False

        return passed


    ##### DELETE TESTS #####

    def test_delete_1(self) :
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        passed = self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.insert(table, vals))
        description=table + " Delete on (" + self.dbutil.format_keyandvals(vals[0]) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return passed and self.maintest(sys._getframe().f_code.co_name, description,
         0 < self.dbutil.delete(table, self.dbutil.format_keyandvals(vals[0])))

    def test_delete_2(self) :
        table=self.table
        self.clear_table(table)
        vals=[('name','AAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Insert for (" + self.dbutil.format_keyvals(vals) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        passed = self.maintest(sys._getframe().f_code.co_name, description,
         self.dbutil.insert(table, vals))
        vals=[('name','ABAA'), ('data', 'ksl;jdfnaskdjnfksjndfiurealksjdf')]
        description=table + " Delete on (" + self.dbutil.format_keyandvals(vals[0]) + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        return passed and self.maintest(sys._getframe().f_code.co_name, description,
          not self.dbutil.delete(table, self.dbutil.format_keyandvals(vals[0])))

    def test_delete_3(self) :
        table=self.table
        self.clear_table(table)
        vals1 =[('name','AAA1'), ('data', 'lksjdfoijeoiwjeosijdlkfsndclns')]
        vals2 = [('name','AAA2'), ('data', '023481098734923')]
        vals3 = [('name','AAA3'), ('data', 'sdlkjflskjdlkfjsld3')]
        vals4 = [('name','BBB3'), ('data', 'fasdafree3433443')]

        vals = [vals1, vals2, vals3, vals4]
        passed=True
        for val in vals :
            description=table + " Insert for (" + self.dbutil.format_keyvals(val) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description, self.dbutil.insert(table, val)) :
                passed=False
        for val in vals :
            description=table + " Delete on (" + self.dbutil.format_keyvals(val[0]) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
                                   self.dbutil.delete(table, self.dbutil.format_keyandvals(val[0]))) :
                passed=False
        return passed


    def test_delete_4(self) :
        table=self.table
        self.clear_table(table)
        vals1 =[('name','AAA1'), ('data', 'lksjdfoijeoiwjeosijdlkfsndclns')]
        vals2 = [('name','AAA2'), ('data', '023481098734923')]
        vals3 = [('name','AAA3'), ('data', 'sdlkjflskjdlkfjsld3')]
        vals4 = [('name','BBB3'), ('data', 'fasdafree3433443')]
        cond = "name like 'AAA%'"

        vals = [vals1, vals2, vals3, vals4]
        passed=True
        for val in vals :
            description=table + " Insert for (" + self.dbutil.format_keyvals(val) + ")"
            self.logteststart(sys._getframe().f_code.co_name, description)
            if not self.maintest(sys._getframe().f_code.co_name, description,
                                   self.dbutil.insert(table, val)) :
             passed=False
        description=table + " Delete on (" + cond + ")"
        self.logteststart(sys._getframe().f_code.co_name, description)
        if not self.maintest(sys._getframe().f_code.co_name, description,
                               3 == self.dbutil.delete(table, cond)) :
            passed=False

        passed = self.maintest(sys._getframe().f_code.co_name, description,
                               1 == len(self.dbutil.query(table, '*', "name like 'BBB3'")))
        return passed
