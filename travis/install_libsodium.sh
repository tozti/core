#!/bin/sh
set -ex
wget https://download.libsodium.org/libsodium/releases/LATEST.tar.gz
tar xzf LATEST.tar.gz 
cd libsodium-stable/
./configure --prefix=/usr
make && make check && sudo make install