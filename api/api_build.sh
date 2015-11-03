cat .ubuntu_install | xargs sudo apt-get install
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Ubuntu Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Ubuntu Requirements Install Failure && return 1
sudo pip install -r .pip_install
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Pip Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Pip Requirements Install Failure && return 1

return 0
