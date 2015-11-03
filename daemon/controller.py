#!/usr/bin/env python

import os, sys, time
from daemon import Daemon
import multiprocessing
import socket
import argparse
from api import queue
from daemon_utils import deploy_container
import subprocess
import daemon_utils
import json

DB_FILE = str()
MAX_VMS = 0
QUEUE_HOST = str()

class Machine(object):
    def __init__(self, hostname, thread_count, ip='None'):
        self.hostname = hostname
        self.thread_count = thread_count
        self.ip = ip

    def to_json(self):
        out = dict()
        out['hostname'] = self.hostname
        out['thread_count'] = self.thread_count
        out['ip'] = self.ip
        return out

class VMLog(object):
    def __init__(self):
        self.machines = list()

    def add(self, hostname, thread_count, ip='None'):
        temp = Machine(hostname, thread_count, ip)
        self.machines.append(temp)

    def to_json(self):
        out = list()
        for i in self.machines:
            out.append(i.to_json())
        return out

    def load_from_file(self, file):
        data = json.load(file)
        for i in data:
            self.add(i['hostname'], i['thread_count'], i['ip'])

def load_imbalance(machs, queue_len):
    cap = 0
    for i in machs.machines:
        cap = cap + i.thread_count
    if (cap > queue_len):
        if(len(machs.machines) + 1 > MAX_VMS):
            print('Too many VMs running.  Cannot create another one.')
            return False
        return True
    return False

class MyDaemon(Daemon):
    def run(self):
        print('Generating queue...')
        q = queue.gen_queue(QUEUE_HOST, 6379, '')
        print('Loading machine database...')
        machs = VMLog()
        if os.path.isfile(DB_FILE) is True:
            print('Opening %s...' % DB_FILE)
            db = open(DB_FILE, 'r')
            machs = VMLog()
            machs.load_from_file(db)
        else:
            print('File does not exist.  Creating...')
            db = open(DB_FILE, 'w+')
            db.write('[]')
            db.close()
        print('Done')
        db.close()

        while True:
            print(len(q))
            if load_imbalance(machs, len(q)):
                print('Starting new instance')
                new_mach_info = daemon_utils.start_vm()
                machs.add(new_mach_info['host_name'],
                          new_mach_info['thread_count'])
                db = open(DB_FILE, 'w')
                db.write(json.dumps(machs.to_json(), indent=2))
                db.close()
            time.sleep(1)





if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Praxyk Control Daemon')
    parser.add_argument('--start', action='store_true')
    parser.add_argument('--stop', action='store_true')
    parser.add_argument('--restart', action='store_true')
    parser.add_argument('--db_file', type=str, required=True)
    parser.add_argument('--max_vms', type=int, required=True)
    parser.add_argument('--queue_host', type=str, required=True)
    args = parser.parse_args()

    DB_FILE = args.db_file
    MAX_VMS = int(args.max_vms)
    QUEUE_HOST = args.queue_host

    daemon = MyDaemon('/tmp/praxyk.pid')
    if args.start:
        print('Starting master control daemon...')
        daemon.start()
    elif args.stop:
        daemon.stop()
    elif args.restart:
        daemon.restart()
