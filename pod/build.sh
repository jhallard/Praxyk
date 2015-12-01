#!/bin/bash

export PRAXYK_POD_DIR=$PWD
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

git submodule update --init --recursive

cd $HOME
sudo apt-get -qqy update
sudo apt-get -qqy install libxml2-dev libarmadillo-dev automake autotools-dev \
libtool cmake swig python-dev libleptonica-dev libicu-dev clang gcc g++ ssh \
libopencv-dev tesseract-ocr-dev libboost-all-dev python-setuptools > .build.log

sudo pip install editdistance

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD Ubuntu Requirements Install Success
[ $RETVAL -ne 0 ] && echo POD Ubuntu Requirements Install Failure && exit 1

cd $HOME
if [ ! -d mlpack ]
then
    git clone https://github.com/mlpack/mlpack.git -b mlpack-1.0.12
    mkdir -p mlpack/build
    cd mlpack
    git apply $PRAXYK_POD_DIR/patches/mlpack_lib_only.patch
    cd build && cmake .. && sudo make install
fi

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD MLPack Requirements Install/Build Success
[ $RETVAL -ne 0 ] && echo POD MLPack Requirements Install Failure && exit 1

cd $HOME
if [ ! -d clandmark ]
then
    git clone https://github.com/Praxyk/clandmark -b praxyk
    mkdir -p clandmark/build
    cd clandmark/build && cmake .. && sudo make install
fi

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD CLandmark Requirements Install/Build Success
[ $RETVAL -ne 0 ] && echo POD CLandmark Requirements Install Failure && exit 1

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH
export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH
sudo ldconfig

cd $PRAXYK_POD_DIR
mkdir -p build
cd build
cmake .. && sudo make install

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD Full Build Success
[ $RETVAL -ne 0 ] && echo POD Full Build Failure && exit 1

sudo ldconfig

python -c "import praxyk"

RETVAL=$?
[ $RETVAL -eq 0 ] && echo Praxyk Python Import Success
[ $RETVAL -ne 0 ] && echo Praxyk Python Import Failure && exit 1

echo "POD Build and Install Process Complete"
exit 0
