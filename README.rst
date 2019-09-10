========
Salt Bin
========

The Salt Bin project is here to allow for single binary builds of Salt
to be easy to make and distribute. Distributing Python applications is
notoriously difficult, and while there are MANY tools that seek to solve
this problem, they can't do it in a universal way.

This project aims to combine multiple tools to build a single, portable
binary for salt.

Usage
=====

Just clone the repo and run `build.py`. 

git clone https://github.com/saltstack/salt-bin.git
cd salt-bin
./build.py

If you want to add extra deps to your build of Salt just copy the
requirements.txt add your deps and then point the build.py script to it
with the `-r` flag.

./build.py -r my-requirements.txt

Dependencies
============

This script requires python 3 and has only been tested on python 3.7
The `staticx` python utility is also required

