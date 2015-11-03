cat api/.ubuntu_install | xargs apt-get -y install
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Ubuntu Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Ubuntu Requirements Install Failure && echo 1
pip install -r api/.pip_install
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Pip Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Pip Requirements Install Failure && echo 1

echo 0
