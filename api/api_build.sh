cat api/.ubuntu_install | xargs sudo apt-get -y install > .build.log
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Ubuntu Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Ubuntu Requirements Install Failure && echo 1
sudo pip install -r api/.pip_install > .build.log
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Pip Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Pip Requirements Install Failure && echo 1

echo 0
