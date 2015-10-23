#!/bin/bash

IMPORT="/home/jhallard/linux/praxyk-api"
SERVER=$(./get_redis_url.py)
echo "Running rqworker with a connection to redis server at " $SERVER
rqworker -u $SERVER  -q --path $1 #$IMPORT
