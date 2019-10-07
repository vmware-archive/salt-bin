#!/bin/bash
PYVER='3.7.4'
PYPRE='3.7'

yum install -y xz libffi-devel bzip2-devel xz-devel ncurses-devel gdbm-devel sqlite-devel readline-devel zlib-devel libuuid-devel
yum groupinstall -y 'Development Tools'

curl -LO  https://www.openssl.org/source/openssl-1.1.1d.tar.gz
tar -xvf openssl-1.1.1d.tar.gz

cd openssl-1.1.1d
./config shared --prefix=/usr/local/openssl11 --openssldir=/usr/local/openssl11 && make && make install
cd ..

curl -LO https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
tar xvf Python-3.7.4.tar.xz
cd Python-3.7.4
# Edit Modules/Setup.dist
LDFLAGS="-Wl,-rpath=/usr/local/openssl11/lib" ./configure --prefix=/usr/local/python37 --with-openssl=/usr/local/openssl11 --with-system-ffi --enable-shared && make && make install
cd ..

ln -s /usr/local/python37/bin/*3.7* /usr/local/bin
ln -s /usr/local/python37/bin/pip3.7 /usr/local/bin/pip3
export LD_LIBRARY_PATH=/usr/local/python37/lib/:/usr/local/openssl11/lib/
LD_LIBRARY_PATH=/usr/local/python37/lib/:/usr/local/openssl11/lib/ pip3 install staticx
ln -s /usr/local/python37/bin/staticx /usr/local/bin/staticx
cd /opt
LD_LIBRARY_PATH=/usr/local/python37/lib/:/usr/local/openssl11/lib/ python3.7 build.py
