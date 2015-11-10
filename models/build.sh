#!/bin/bash

# @author John Allard, Nick Corgan, others
# @github https://github.com/Praxyk/praxyk

# this script installs, builds, and initializes a local MySQL instance and a
# redis database instance, both running on localhost at default ports

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -q -y install mysql-server
sudo service mysql restart
mysql -e "create database IF NOT EXISTS test;" -uroot

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Models: MySQL Requirements Install Success"
[ $RETVAL -ne 0 ] && echo "  Models : MySQL Requirements Install Failure" && exit 1

sudo apt-get -y install redis-server
sudo service redis-server restart

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  Models: Redis Requirements Install Success"
[ $RETVAL -ne 0 ] && echo "  Models : Redis Requirements Install Failure" && exit 1

exit 0
