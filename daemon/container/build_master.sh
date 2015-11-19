#!/bin/bash
./docker_config.py --worker_config config.py --branch master
time ./build.sh > >(tee -i praxyk_log.txt)
if [ $? != 0 ]; then
  echo "Error: docker build command failed."
  exit 1
  mail -s "Praxyk master build - FAIL" mvincent@praxyk.com << praxyk_log.txt
fi
docker push tekgek/praxyk:latest
mail -s "Praxyk master build - PASS" mvincent@praxyk.com << praxyk_log.txt
