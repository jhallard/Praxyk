#!/bin/bash

export PRAXYK_POD_DIR=$PWD
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

cd $HOME
sudo apt-get install -y libboost-math-dev libboost-program-options-dev libboost-random-dev \
libboost-test-dev libxml2-dev libarmadillo-dev automake autotools-dev libtool cmake swig python-dev \
libleptonica-dev libfann-dev libicu-dev libpango1.0-dev libcairo2-dev libboost-thread-dev \
clang gcc g++ ssh libopencv-dev

git clone https://github.com/tesseract-ocr/tesseract -b 3.02.02
cd tesseract
./autogen.sh
./configure
sudo make install

cd $HOME
git clone https://github.com/tesseract-ocr/tessdata
sudo cp -r tessdata/* /usr/local/share/tessdata

git clone https://github.com/mlpack/mlpack.git -b mlpack-1.0.12
mkdir mlpack/build
cd mlpack/build
cmake ..
sudo make install

echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> $HOME/.bashrc
sudo ldconfig

cd $PRAXYK_POD_DIR
mkdir -p build
cd build
cmake ..
sudo make install

sudo ldconfig
