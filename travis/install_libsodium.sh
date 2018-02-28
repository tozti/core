#!/bin/sh
set -ex
mkdir -p libsodium
cd libsodium
wget -O new.tar.gz https://download.libsodium.org/libsodium/releases/LATEST.tar.gz
if [ ! -f old.tar.gz ] || [ $( cmp -s new.tar.gz old.tar.gz) ]; then
    tar xzf new.tar.gz 
    cd libsodium-stable/
    ./configure --prefix=/usr
    make && make check
else
    cd libsodium-stable/
fi
sudo make install
cd ..
mv new.tar.gz old.tar.gz