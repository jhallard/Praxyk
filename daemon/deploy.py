from __future__ import print_function
import sys
import os
import subprocess

def deploy_container(host_addr):
    print('Running docker container praxyk-latest...')
    command = ['docker', 'run', 'praxyk:latest']
    try:
        pipe = subprocess.Popen(command)
    except Exception as e:
        print('Error: %s' % str(e))
        return 1
    return 0
