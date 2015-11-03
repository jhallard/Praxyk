from __future__ import print_function
import sys
import os
import subprocess
import paramiko
import json
from scp import SCPClient

def deploy_container():
    print('Running docker container praxyk:latest...')
    command = ['docker', 'run', '-d', 'praxyk:latest']
    try:
        pipe = subprocess.Popen(command)
    except Exception as e:
        print('Error: %s' % str(e))
        return 1
    return 0

def start_vm():
    """
    /XXX Code to get VM instance info and start it goes here
    Note: root access required for this to work. (Preferably login as root
    through ssh)
    """

    dummy_ip = '127.0.0.1'
    dummy_user='mike'
    dummy_password='password'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(dummy_ip, username=dummy_user, password=dummy_password)

    scp = SCPClient(ssh.get_transport())

    stdin, stdout, stderr = ssh.exec_command('echo $HOME')
    homedir = stdout.readlines()[0]
    homedir = homedir.replace('\n', '') + '/'
    scp.put('local.py', homedir + 'vm_init.py')

    stdin, stdout, stderr = ssh.exec_command(homedir + 'vm_init.py')
    info = json.loads(stdout.readlines()[0])
    return info
