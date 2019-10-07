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

* git clone https://github.com/saltstack/salt-bin.git
* cd salt-bin
* ./build.py

If you want to add extra deps to your build of Salt just copy the
requirements.txt add your deps and then point the build.py script to it
with the `-r` flag.

* ./build.py -r my-requirements.txt

Docker Build
============

It may be desireable to build the binary in a docker container. For instance
building in a centos 6 container should product a more portable binary.

`salt-bin` comes with a script for building  in centos 6 with a newer python.
To build make a new docker container:

docker run -it centos:6 bash

Then copy the files into the container:

docker cp . <container name>:/opt

Then run the build:

cd /opt

bash scripts/cent6_setup.sh

The results will be in the dist directory where they can be coppied back out with
the docker cp command:

docker cp <container name>:/opt/dist .

