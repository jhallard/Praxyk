#!/bin/bash
./docker_config.py --worker_config config.py --branch master
./build.sh
if [ $? != 0 ]; then
  echo "Error: docker build command failed."
  exit 1
fi
