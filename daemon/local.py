#!/usr/bin/python
from __future__ import print_function
import os
import sys
import json
import socket
import subprocess
import multiprocessing

def get_machinfo():
    """
    Returns a JSON-parsable dict object with the following:
    * hostname ('host_name')
    * Number of cores ('thread_count')
    """

    out = dict()
    out['host_name'] = socket.gethostname()
    out['thread_count'] = multiprocessing.cpu_count()

    return out

def run_containers():
    info = get_machinfo()
    print(json.dumps(info))
    command_aptget_update = ['apt-get', 'update']
    command_get_docker = ['apt-get' , 'install', '-y', 'docker.io']
    command_pull = ['docker', 'pull', 'tekgek/praxyk']
    command_run = ['docker', 'run', '-d', 'tekgek/praxyk:latest']

    log = open('praxyk.log', 'w')
    subprocess.call(command_aptget_update, stdout=log, stderr=log)
    subprocess.call(command_get_docker, stdout=log, stderr=log)
    subprocess.call(command_pull, stdout=log)
    for i in range(0, info['thread_count']):
        subprocess.call(command_run, stdout=log)

run_containers()
