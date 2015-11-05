# @author John Allard
# @github https://github.com/Praxyk/praxyk

# this script installs and builds all system wide (ubuntu) and python level
# requirements needed by the API server

touch api/.build.log
xargs sudo apt-get -y install < api/.ubuntu_install > api/.build.log
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Ubuntu Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Ubuntu Requirements Install Failure && exit 1

sudo pip install -r api/.pip_install > api/.build.log
RETVAL=$?
[ $RETVAL -eq 0 ] && echo API Pip Requirements Install Success
[ $RETVAL -ne 0 ] && echo API Pip Requirements Install Failure && exit 1

exit 0
