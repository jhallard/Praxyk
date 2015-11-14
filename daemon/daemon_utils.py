from __future__ import print_function
import sys
import os
import subprocess
import paramiko
import json
import string
import random
import time
from devops_client import create_instance
from scp import SCPClient

def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def deploy_container():
    print('Running docker container praxyk:latest...')
    command = ['docker', 'run', '-d', 'praxyk:latest']
    try:
        pipe = subprocess.Popen(command)
    except Exception as e:
        print('Error: %s' % str(e))
        return 1
    return 0

def start_vm(working_path):
    name = 'docker-worker-' + id_generator()

    print('Creating docker worker with name %s' % name)
    mach_data = create_instance(name,ret_json=True)
    time.sleep(10)
    print('Done.  Running setup...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to root@%s' % mach_data['instance']['ip'])
    ssh.connect(mach_data['instance']['ip'], username='root', key_filename='/home/mike/.ssh/id_rsa')

    scp = SCPClient(ssh.get_transport())

    stdin, stdout, stderr = ssh.exec_command('echo $HOME')
    homedir = stdout.readlines()[0]
    homedir = homedir.replace('\n', '') + '/'
    scp.put(working_path + '/' + 'local.py', homedir + 'vm_init.py')

    stdin, stdout, stderr = ssh.exec_command(homedir + 'vm_init.py')
    info = json.loads(stdout.readlines()[0])
    return info
