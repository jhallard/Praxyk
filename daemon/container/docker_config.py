#!/usr/bin/python
from __future__ import print_function
import sys
import os
import argparse

docker_config_file = ["""FROM ubuntu
RUN apt-get update
RUN apt-get install -y git-core python-pip
RUN pip install rq
RUN git clone git://github.com/jhallard/Praxyk -b """,
"""RUN cd Praxyk/pod && ./pod_build.sh
RUN cp -r Praxyk/api /
RUN mkdir -p /drive1/img_store""",
"""EXPOSE 6379
CMD cd / && rqworker -c """]

worker_run = 'rqworker -c '

parser = argparse.ArgumentParser(description='Praxyk Container Configurator')
parser.add_argument('--worker_config', type=str, required=True)
parser.add_argument('--branch', type=str, required=True)
args = parser.parse_args()

include_string = '\nADD ' + args.worker_config + ' /' + args.worker_config

processed = os.path.basename(args.worker_config).replace('.py', '')

docker_config_file[0] = docker_config_file[0] + args.branch
docker_config_file[1] = docker_config_file[1] + include_string
docker_config_file[2] = docker_config_file[2] + processed

out = open('Dockerfile', 'w+')
for i in docker_config_file:
    out.write(i + '\n')

out.close()
