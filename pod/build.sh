#!/bin/bash

export PRAXYK_POD_DIR=$PWD
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

cd $HOME
sudo apt-get -qqy update
sudo apt-get -qqy install libboost-math-dev libboost-program-options-dev libboost-random-dev \
libboost-test-dev libxml2-dev libarmadillo-dev automake autotools-dev libtool cmake swig python-dev \
libleptonica-dev libfann-dev libicu-dev libpango1.0-dev libcairo2-dev libboost-thread-dev \
clang gcc g++ ssh libopencv-dev > .build.log 

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD Ubuntu Requirements Install Success
[ $RETVAL -ne 0 ] && echo POD Ubuntu Requirements Install Failure && exit 1

git clone https://github.com/tesseract-ocr/tesseract -b 3.02.02
cd tesseract && ./autogen.sh && ./configure && sudo make install > .build.log 2>&1

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD Tesseract Requirements Install Success
[ $RETVAL -ne 0 ] && echo POD Tesseract Requirements Install Failure && exit 1

cd $HOME
git clone https://github.com/mlpack/mlpack.git -b mlpack-1.0.12
mkdir -p mlpack/build
cd mlpack
git apply $PRAXYK_POD_DIR/patches/mlpack_lib_only.patch
cd build && cmake .. && sudo make install > .build.log 2>&1

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD MLPack Requirements Install/Build Success
[ $RETVAL -ne 0 ] && echo POD MLPack Requirements Install Failure && exit 1

cd $HOME
git clone https://github.com/Praxyk/clandmark -b praxyk
mkdir -p clandmark/build
cd clandmark/build && cmake .. && sudo make install > .build.log 2>&1

RETVAL=$?
[ $RETVAL -eq 0 ] && echo POD CLandmark Requirements Install/Build Success
[ $RETVAL -ne 0 ] && echo POD CLandmark Requirements Install Failure && exit 1

echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> $HOME/.bashrc
echo 'export PYTHONPATH=/usr/local/lib/python2.7/dist-packages:$PYTHONPATH' >> $HOME/.bashrc
sudo ldconfig

cd $PRAXYK_POD_DIR
mkdir -p build
cd build
cmake .. && sudo make install > .build.log

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
