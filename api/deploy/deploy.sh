#!/bin/bash

# @author John Allard, Nick Corgan, others
# @github https://github.com/Praxyk/praxyk

# this script takes the API server code and deploys it as a wsgi script running
# under an apache server on port 80.

echo "Deploying Praxyk API Server"

xargs sudo apt-get -y install < .ubuntu_install

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  API-Deploy : Ubuntu Requirements Install Success"
[ $RETVAL -ne 0 ] && echo "  API-Deploy : Ubuntu Requirements Install Failure" && exit 1

sudo a2enmod wsgi 

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  API-Deploy : Apache WSGI Enabled"
[ $RETVAL -ne 0 ] && echo "  API-Deploy : Apache WSGI Failure" && exit 1

$SERVER_IP=$(ifconfig eth0 | grep inet | awk '{ print $2 }')

sudo mkdir /var/www/praxyk_api_server
sudo cp api_server.wsgi /var/www/praxyk_api_server/
sudo cp api.praxyk.com.conf /etc/apache2/sites-available/api.praxyk.com.conf

sudo service apache2 restart

sudo a2ensite api.praxyk.com.conf

RETVAL=$?
[ $RETVAL -eq 0 ] && echo "  API-Deploy : Apache Site Started"
[ $RETVAL -ne 0 ] && echo "  API-Deploy : Apache Site Start Failure" && exit 1


exit 0
