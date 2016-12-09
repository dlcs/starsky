#!/bin/bash
apt-get update -y && apt-get install -y wget libpng-dev libjpeg-dev libtiff-dev zlib1g-dev gcc g++ autoconf automake libtool checkinstall python-pip python-dev build-essential
wget http://www.leptonica.org/source/leptonica-1.72.tar.gz
tar -xzvf leptonica-1.72.tar.gz
cd leptonica-1.72
./configure
make
make install
cd ..
wget https://github.com/tesseract-ocr/tesseract/archive/3.04.01.tar.gz
tar -xzvf 3.04.01.tar.gz
cd tesseract-3.04.01/
./autogen.sh
./configure
make
make install