#!/bin/bash

export LD_LIBRARY_PATH=/home/jhallard/linux/praxyk-api/pod/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/home/jhallard/linux/praxyk-api/pod/python:$PYTHONPATH

/usr/bin/python2 /home/jhallard/linux/praxyk-api/pod/tests/pod_spam_test.py
