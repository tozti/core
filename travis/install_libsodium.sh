#!/bin/sh
mkdir -p libsodium
cd libsodium
export LIBSODIUM_PREFIX=$(pwd)
wget -O new.tar.gz https://download.libsodium.org/libsodium/releases/LATEST.tar.gz
if [ ! -f old.tar.gz ] || [ $( cmp -s new.tar.gz old.tar.gz) ] || [ ! -f lib/libsodium.so ]; then
    tar xzf new.tar.gz 
    cd libsodium-stable/
    ./configure --prefix=$LIBSODIUM_PREFIX
    make && make check
else
    cd libsodium-stable
fi
make install
cd ..
mv new.tar.gz old.tar.gz
cd ..