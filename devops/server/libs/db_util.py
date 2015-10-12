#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import MySQLdb
import getpass
import datetime
import os.path
import os
import socket
import sys

#################################################################################################
# Class dbUtil                                                                                   #
#                                                                                                #
# This class is the interface between an application and a mySQL database. It is a wrapper       #
# around the python MySQLdb library that includes an extensive logging system for testing        #
# and validation purposes.                                                                       #
#                                                                                                #
#                                                                                                #
# Arguments : A dictionary of arguments, all of which must be supplied for initialization        #
# to work. Any out of bounds args will cause exceptions to be thrown and errors logged           #
#                                                                                                #
# user      --> str   : The username for the database being used                                 #
# dbip      --> str   : The ip address for the database being used                               #
# pw        --> str   : The password for the database                                            #
# dbname    --> str   : The name of the database we are connecting to/creating                   #
# logclient --> str   : the client string that this class uses to send logs to the logutil mem.  #
# logutil   --> str   : the logutil object that will take the log messages from this object.     #
#                                                                                                #
#                                                                                                #
# Operations - Query, Insert, Update, Delete, Create (table, database),                          #
#              Drop (table, database), build database                                            #
#                                                                                                #
# Note that arguments need to be formatted as lists of tuples to work with most of the           #
# of the functions in this lib (like [('key', 'value'), ... ,('key', 'value)] ), these will      #
# be formatted using the MySQLdb sanitization function and be formatted appropriately            #
#                                                                                                #
##################################################################################################

class dbUtil :

    # @info - takes a map of arguments which supply all info to connect to a database, including
    #         a username, db ip address, and a password.
    def __init__(self, args) :
        self.DB_USER=args['user']
        self.dbip=args['dbip']
        self.dbipv6=args['dbipv6']
        self.logclient = args['logclient']
        self.logger = args['logutil']
        self.PW=args['pw']
        self.db=None

    ##### SET/GET UTILS #####

    def set_user(self, user) :
        self.DB_USER = user

    def set_db_ip(self, ip) :
        self.dbip = ip

    def set_pw(self, pw) :
        self.PW=pw

    def close(self) :
        if self.db :
            self.db.close()


    ##### LOGIN #####

    def login(self) :
        self.db_logf('NEW CONNECTION', 'a', ['DB_IP', 'LOGIN-IP', 'USER'],
                     (self.dbip, socket.getfqdn(), self.DB_USER) )
        ps= self.PW 
        self.db = MySQLdb.connect(host=self.dbip, user=self.DB_USER, passwd=ps, charset='utf8')

        if self.db :
            self.db_logf('NEW CONNECTION', 's', ['DB_IP', 'LOGIN-IP', 'USER'],
                         (self.dbip, socket.getfqdn(), self.DB_USER) )
        else :
            self.db_logf('NEW CONNECTION', 'f', ['DB_IP', 'LOGIN-IP', 'USER'],
                         (self.dbip, socket.getfqdn(), self.DB_USER) )
        return self.db


    ##### DB-INTERFACE QUERY, INSERT, UPDATE, DELETE #####

    def check_if_exists(self, table, cond=None) :
        return self.query(table, '1', cond)


    def query(self, table, rows, cond=None, order_by=None, limit=None) :
        if not cond :
            inp = '''SELECT %s FROM %s''' %  (rows, table)
        else :
            inp = '''SELECT %s FROM %s WHERE (%s)''' %  (rows, table, cond)

        if order_by != None :
            inp = inp + (''' ORDER BY %s ''' % (order_by) )
        if limit != None :
            inp = inp + ('''LIMIT %s ''' % (str(limit)) )

        inp += ';'

        self.log_db_raw(inp)
        try :
            cur = self.db.cursor()
            if cur.execute(inp) :
                results = cur.fetchall()
                self.log_db_query(table, rows, cond, len(results) )
                cur.close()
                return results
            else :
                cur.close()
                self.log_db_query(table, rows, cond, 0)
                return []
        except Exception, e :
            self.log_except(str(sys._getframe().f_code.co_name), inp, str(e))

    def subquery(self, table, rows='*', cond=None, order_by=None, limit=None) :
        # inp = '''( SELECT %s FROM %s WHERE (%s) ) a ''' %  (rows, table, cond)
        if not cond :
            inp = '''( SELECT %s FROM %s''' %  (rows, table)
        else :
            inp = '''( SELECT %s FROM %s WHERE (%s)''' %  (rows, table, cond)

        if order_by :
            inp = inp + (''' ORDER BY %s ''' % (order_by) )
        if limit :
            inp = inp + ('''LIMIT %s ''' % (str(limit)) )

        inp += ' ) a'
        self.log_db_raw(inp)
        return inp


    def insert_or_update(self, table, vals, cond) :
        if not self.insert(table, vals) :
            return self.update(table, vals, cond)
        return True


    def insert(self, table, vals) :
        cur = self.db.cursor()
        vals_str = self.format_vals(vals)
        # if not self.check_if_exists(table, cond) :
        inp = """INSERT INTO %s VALUES ( %s );""" % (table, vals_str)
        self.log_db_raw(inp)
        try :
            if cur.execute(inp) : #tinp + vinp, vals_str) :
                self.db.commit()
                self.log_db_insert(table, vals_str)
                cur.close()
                return True
            else :
                self.log_db_insert(table, vals_str, self.format_keyandvals(vals), False)
                return False
        except Exception, e :
            self.log_except(str(sys._getframe().f_code.co_name), inp, str(e))
            return False


    def update(self, table, vals, cond) :
        cur = self.db.cursor()
        vals_str = self.format_keyvals(vals)

        if self.check_if_exists(table, cond) :
            inp = """UPDATE %s SET %s WHERE (%s);""" % (table, vals_str, cond)
            self.log_db_raw(inp)
            try :
                if cur.execute(inp) :
                    self.db.commit()
                    self.log_db_update(table, vals_str, cond)
                    return True
                else :
                    self.log_db_update(table, vals_str, cond, False) # self.format_keyandvals(vals), False)
                    return False
            except Exception, e :
                self.log_except(str(sys._getframe().f_code.co_name), inp, str(e))

        else :
            self.log_db_update(table, vals_str, self.format_keyandvals(vals), False)
            return False

    def delete(self, table, cond) :
        cur = self.db.cursor()
        cond_str = cond

        inp = """DELETE FROM %s WHERE (%s);""" % (table, cond_str)
        self.log_db_raw(inp)
        try :
            num_del = cur.execute(inp)
            cur.close()
            if num_del > 0 :
                self.db.commit()
                self.log_db_delete(table,  cond_str, num_del)
                return num_del
            else :
                self.log_db_delete(table, cond_str, 0)
                return 0
        except Exception, e :
            self.log_except(str(sys._getframe().f_code.co_name), inp, str(e))
            self.log_db_delete(table, cond_str, 0)
            return 0

    def create_index(self, table, index_name, index_vals) :
        cur = self.db.cursor()
        inp = """CREATE INDEX %s ON %s (%s);""" % (index_name, table, index_vals)
        if not self.index_exists(table, index_name) :
            self.log_db_raw(inp)
            cur.execute(inp)
            cur.close()
            if self.index_exists(table, index_name) :
                self.db.commit()
                self.log_index_create(table, index_name, index_vals)
                return True
            else :
                self.log_index_create(table, index_name, index_vals, False)
                return False
        return False


    def drop_index(self, table, index_name) :
        cur = self.db.cursor()
        inp = """DROP INDEX %s ON %s;""" % (index_name, table)
        self.log_db_raw(inp)
        if self.index_exists(table, index_name) :
            cur.execute(inp)
            cur.close()
            if not self.index_exists(table, index_name) :
                self.db.commit()
                self.log_index_drop(table, index_name)
                return True
            else :
                self.log_index_drop(table, index_name,  False)
                return False
        return False
        

    def index_exists(self, table, index_name) :
        cur = self.db.cursor()
        inp = """SHOW indexes FROM %s WHERE Key_name='%s'""";
        inp = inp % (table, index_name)
        self.log_db_raw(inp)
        cur.execute(inp)
        fetch = cur.fetchall()
        cur.close()
        return len(fetch) > 0 


    def create_table(self, table, rows) :
        cur = self.db.cursor()
        vals_str = self.format_keys(rows)
        inp = """CREATE TABLE %s (%s);""" % (table, vals_str)
        if not self.table_exists(table) :
            try :
                self.log_db_raw(inp)
                cur.execute(inp)
                cur.close()
                if self.table_exists(table) : # if the table now exists
                    self.db.commit()
                    self.log_db_table_create(table, vals_str)
                    return True
                else :
                    self.log_db_table_create(table, vals_str, False)
                    return False
            except Exception, e :
                self.log_except(str(sys._getframe().f_code.co_name), inp, str(e))
                self.log_db_table_create(table, vals_str, False)
                return False
        else :
            self.log_db_table_create(table, vals_str, False)
            return False


    def drop_table(self, table) :
        cur = self.db.cursor()
        if self.table_exists(table) :
            inp = """DROP TABLE %s; """ % (table)
            self.log_db_raw(inp)
            cur.execute(inp)
            cur.close()
            self.db.commit()
            if not self.table_exists(table) :
                self.log_db_table_drop(table)
                return True
            else :
                self.log_db_table_drop(table, False)
                return False
        else :
            cur.close()
            self.log_db_table_drop(table, False)
            return False

    def table_exists(self, table) :
        cur = self.db.cursor()
        subq = '''SHOW TABLES LIKE '%s' ''' % table
        self.log_db_raw(subq)
        cur.execute(subq)
        res = cur.fetchall()
        cur.close()
        return len(res) > 0

    def create_database(self, name) :
        cur = self.db.cursor()
        if not self.database_exists(name) :
            inp = """CREATE DATABASE %s; """ % (name)
            self.log_db_raw(inp)
            cur.execute(inp)
            cur.close()
            if self.database_exists(name) :
                self.db.commit()
                self.log_db_database_create(name)
                return True
            else :
                self.log_db_database_create(name, False)
                return False
        else :
            self.log_db_database_create(name, False)
            cur.close()
            return False

    def drop_database(self, name) :
        cur = self.db.cursor()
        if self.database_exists(name) :
            inp = """DROP DATABASE %s; """ % (name)
            self.log_db_raw(inp)
            cur.execute(inp)
            cur.close()
            self.db.commit()
            if not self.database_exists(name) :
                self.log_db_database_drop(name)
                return True
            else :
                self.log_db_database_drop(name, False)
                return False
        else :
            cur.close()
            self.log_db_database_drop(name, False)
            return False

    def database_exists(self, dbname) :
        cur = self.db.cursor()
        subq = '''SHOW DATABASES LIKE '%s' ''' % dbname
        self.log_db_raw(subq)
        try :
            cur.execute(subq)
            res = cur.fetchall()
            cur.close()
            return len(res) > 0
        except Exception, e :
            cur.close()
            self.log_except(str(sys._getframe().f_code.co_name), str(schema), str(e))
            return False


    def use_database(self, name) :
        cur = self.db.cursor()
        if self.database_exists(name) :
            inp = """USE  %s; """ % (name)
            self.log_db_raw(inp)
            cur.execute(inp)
            self.db.commit()
            self.log_db_database_use(name)
            cur.close()
            return True
        else :
            self.log_db_database_use(name, False)
            cur.close()
            return False


    def build_database(self, schema) :
        dbname = schema['dbname']
        self.db_logf('BUILD DATABASE', 'w', ['database', 'schema'], (dbname, schema))

        if not self.create_database(dbname) :
            self.log_db_database_build(dbname, schema, False)
            return False

        if not self.use_database(dbname) :
            self.log_db_database_build(dbname, schema, False)
            self.db_logf('BUILD DATABASE', 'a', ['Schema'], str(schema['dbname']), 'Failed to Use After Build')
            return False

        for table in schema['tables'] :
            rows = schema['rows'][table]
            rows = [[row] for row in rows]   # need to encase it in a list

            indexes = []
            if table in schema['indexes'] :
                indexes = schema['indexes'][table]

            if not isinstance(indexes, list) :
                indexes = [indexes]

            try :
                if not self.create_table(table, rows) :
                    self.log_db_database_build(dbname, schema, False)
                    return False
                
                for index in indexes :
                    if not self.create_index(table, index[0], index[1]) :
                        self.log_db_database_build(dbname, schema, False)
                        return False
            except Exception, e :
                self.log_except(str(sys._getframe().f_code.co_name), str(schema), str(e))
                self.log_db_database_build(dbname, schema, False)
                return False

        self.log_db_database_build(dbname, schema)
        return True






    ############# ARGUMENT FORMATTING ############

    # formats list of tuple pairs as "k0='v0',k1='v1, ... ,kn='vn'" for n in len(vals_list)
    def format_keyvals(self, vals_list) :
        vals_str = ''
        if not vals_list :
            self.db_logf('FORMAT Attempt', 'f', ['vals_list'],  'empty')
            return
        if not isinstance(vals_list, list) :
            vals_list = [vals_list]

        for item in vals_list :
            val = MySQLdb.escape_string(str(item[1]))
            key = MySQLdb.escape_string(str(item[0]))
            vals_str += ("%s='%s'," % (key,val))
        return vals_str[:-1] # remove last comma

    # formats list of tuple pairs as "k0='v0' and k1='v1 and  ...  and kn='vn'" for n in len(vals_list)
    def format_keyandvals(self, vals_list) :
        return self.format_keyvals(vals_list).replace(","," and ")

    # formats list of tuple pairs as "v0, v1, ... ,vn" for n in len(vals_list)
    def format_vals(self, vals_list) :
        vals_str = ''
        if not vals_list :
            self.db_logf('FORMAT Attempt', 'f', ['vals_list'],  'empty')
            return ""
        if not isinstance(vals_list, list) :
            vals_list = [vals_list]

        for item in vals_list :
            val = MySQLdb.escape_string(str(item[1]))
            vals_str += ("'%s'," % val)
        return vals_str[:-1] # remove last comma

    # formats list of tuple pairs as "k0, k1, ... , kn" for n in len(vals_list)
    def format_keys(self, vals_list) :
        vals_str = ''
        if not vals_list :
            self.db_logf('FORMAT Attempt', 'f', ['vals_list'],  'empty')
            return ""
        if not isinstance(vals_list, list) :
            vals_list = [vals_list]
        for item in vals_list :
            key = MySQLdb.escape_string(str(item[0]))
            vals_str += ("%s," % key)
        return vals_str[:-1] # remove last comma

    def convert_timestr(self, timestr) :
        dt = datetime
        ret = dt.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ")
        return ret.strftime('%Y-%m-%d %H:%M:%S')




    ################# LOGGING UTILITIES #########################

    def db_logf(self, head, status, valnames=[], vals="", notes="") :
        if not self.logger :
            valstr = ""
            for val in valnames :
                valstr += (val + " : (%s) ")
            if vals :
                valstr = valstr % vals
            print head + " " + status + " " + valstr +  " :: " + notes
            return
        if isinstance(vals, list) :
            for val in vals :
                if len(str(val)) > 2000 :
                    val = val[:2000]
        return self.logger.log_event(self.logclient, head, status, valnames, vals, notes)

    def log_db_raw(self, raw) :
        if len(raw) > 200 :
            raw = raw[:200]
        self.db_logf("RAW DB-INPUT",'i',['Input : '], str(raw))

    def log_db_update(self, table, vals, cond="", success=True) :
        outcome = 's' if success else 'f'
        condname = '' if cond=="" else 'cond'
        return self.db_logf('UPDATE', outcome, ['table', ' vals', 'cond'], (table, vals, cond))

    def log_db_insert(self, table, vals, cond="", success=True) :
        outcome = 's' if success else 'f'
        condname = '' if cond=="" else 'cond'
        return self.db_logf('INSERT', outcome, ['table', ' vals', 'cond'], (table, vals, cond))

    def log_db_query(self, table, rows, cond, number) :
        return self.db_logf('QUERY', 'i', ['table', 'rows', 'cond', '#Hits'], (table, rows, cond, number))

    def log_db_delete(self, table, cond, number) :
        outcome = 's' if number > 0 else 'f'
        return self.db_logf('DELETE', outcome, ['table', 'cond', '#Hits'], (table, cond, number))

    def log_index_create(self, table, indexn, indexv, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('CREATE INDEX', outcome, ['table', 'Index Name', 'Index Vals'], (table, indexn, indexv))

    def log_index_drop(self, table, indexn, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('DROP INDEX', outcome, ['table', 'Index Name'], (table, indexn))

    def log_db_table_create(self, table, rows, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('CREATE TABLE', outcome, ['table', 'rows'], (table, rows))

    def log_db_table_drop(self, table, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('DROP TABLE', outcome, ['table'], (table))


    def log_db_index_create(self, table, index, rows, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('CREATE INDEX', outcome, ['table', 'index', 'rows'], (table, index, vals))

    def log_db_index_drop(self, table, index, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('DROP INDEX', outcome, ['table', 'index'], (table, index))


    def log_db_database_create(self, database, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('CREATE DATABASE', outcome, ['database'], (database))

    def log_db_database_drop(self, database, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('DROP DATABASE', outcome, ['database'], (database))

    def log_db_database_use(self, database, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('USE DATABASE', outcome, ['database'], (database))

    def log_db_database_build(self, database, schema, success=True) :
        outcome = 's' if success else 'f'
        return self.db_logf('BUILD DATABASE', outcome, ['database', 'schema'], (database, schema))

    def log_except(self, fn, query, exn) :
        outcome = 'f'
        return self.db_logf('EXCEPTION', outcome, ['function', 'self.query', '\n\te.what'], (fn, query, str(exn)))
