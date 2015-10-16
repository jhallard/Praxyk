#!/usr/bin/env python

## @auth John Allard
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

from sys import *
import sys
import datetime
import os
import os.path

class logUtil :

    # @info - takes a map : client_name --> (filename | sys.std*)
    # Every user of the class will add a client name, and every time
    # they log they'll submit their name. This is a key to a list of outputs,
    # and this class writes the logs to them appropriately.
    def __init__(self, clients={}) :
        self.mclients = clients
        self.combined_client_name='combined'
        self.error_client_name='stderr'
        self.statusmap = {
                     'a':'Attempting',
                     's':'Success   ',
                     'f':'Failed    ',
                     'w':'Warning   ',
                     'e':'Exception ',
                     'i':'Info      ',
                     '' :'          '
                     }
        # maps a status code to a return value (ex 's' -> true)
        self.retmap   = lambda x : not x or x in 'aswi '

    # @info - takes a name and a list of filenames or sys.std*s, then adds
    # an entry to our clients dictionary as (name --> [outputs])
    def add_client(self, name, logf=[sys.stdout]) :
        if not isinstance(logf, list) :
            logf = [log]
        self.mclients[name]=logf

    # @info - reset our clients map from scratch
    def set_clients(self, clients) :
        self.mclients = clients

    # @info - this is the general logging function
    # It must take a client, then a single string containing the actual text
    # to be logged. The last argument is optional, if true we append a timestamp
    # to the log in the form HH:MM:SS:XXX
    # The logstring will be logged to all of in the list that the client maps to.
    def log(self, client, logstr, time=True) :
        dt = self.timestamp() + ' : ' if time else ""
        if client not in self.mclients :
            return False

        for fh in self.mclients[client] :
            f = self.sopen(fh)
            f.write(dt + logstr + '\n')
            self.sclose(f)

        if self.combined_client_name in self.mclients :
            for fh in self.mclients[self.combined_client_name] :
                f = self.sopen(fh)
                f.write(dt + self.append_client(client, logstr) + '\n')
                self.sclose(f)

    # @info - log a block of information, possibly with values to be subtituted.
    #         No timestamp to be added.
    def logblock(self, client, block, vals=None) :
        if vals :
            block = block % vals

        self.log(client, block, False)

    # @info - a wrapper around the log function to handle the common case of logging events like
    #         'success', 'failed', 'attempting', etc. Takes a header, the log context, a client, a
    #         status (see self.statusmap), a list of strings that name the values to be substituted.
    #         finally can contain a note on the end.
    def log_event(self, client, head, status, valnames=[], vals=None, notes="") :
        headspace = 0 if len(head) >=24 else 24 - len(head)
        head  += headspace*' '+'| '

        status_m = self.statusmap[status]

        if notes :
            notes = ' | Notes : ' + notes

        valstr=''
        if vals :
            valstr = ' | '
            for val in valnames :
                valstr += ' ' + val + ' (%s) '
            valstr = valstr % vals

        # if it's a failure or exception also log to our stderr client
        if status == 'e' or status == 'f':
            logstr = self.append_client(client, head+status_m+valstr+notes)
            self.log(self.error_client_name, logstr)

        self.log(client, head+status_m+valstr+notes)
        return self.retmap(status)

    # @info - this function can be used to append a client name to a log string. This is normally used
    #         when multiple clients are logging to the same stream, in which case an identifer (client name)
    #         is appended to each log.
    def append_client(self, client, logstr) :
        clientspace = 0 if len(client) >=15 else 15 - len(client)
        return ' [' + client + '] ' + clientspace*' ' + logstr

    # @info - get the current time in the form HH:MM:SS.123
    def timestamp(self) :
        return  str(datetime.datetime.now()).split(' ')[1][:-3]

    def date_timestamp_str(self) :
        dt = datetime.datetime.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')


    def get_file_names(self) :
        file_list = []
        for key,val in self.mclients.iteritems() :
            for fh in val :
                if fh is not sys.stdout and fh is not sys.stderr :
                    file_list.append(fh)

        return list(set(file_list))



    # @info - 'smart-open' function that accept a 'filename' and opens it if it corresponds to a file or just returns
    #         it if it is sys.stdout or sys.stderr. This allows us to treat std streams and files with the same code.
    def sopen(self, filename):
        fh = None
        if filename and filename is not sys.stdout and filename is not sys.stderr :
            if os.path.isfile(filename) :
                fh = open(filename, 'a+')
            else :
                fh = open(filename, 'wr+')
        else:
            fh = sys.stdout
        return fh
    
    # @info - corresponding close function, only calls close on a file if it is an actual file and not stdout or sterr
    def sclose(self, fh) :
        if fh is not sys.stdout and fh is not sys.stderr:
            fh.close()
