#!/bin/bash

export PRAXYK_POD_DIR=$PWD
export CC=/usr/bin/clang
export CXX=/usr/bin/clang++

cd $HOME
sudo apt-get install clang automake libtool cmake swig python-dev libleptonica-dev libfann-dev libicu-dev libpango1.0-dev libcairo2-dev libboost-thread-dev
git clone https://github.com/tesseract-ocr/tesseract -b 3.02.02
cd tesseract
./autogen.sh
./configure
sudo make -j2 install
cd $HOME
git clone https://github.com/tesseract-ocr/tessdata
sudo cp -rv tessdata/* /usr/local/share/tessdata

echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> $HOME/.bashrc
sudo ldconfig

cd $PRAXYK_POD_DIR
mkdir -p build
cd build
cmake ..
sudo make install

sudo ldconfig
