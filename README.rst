========
Salt Bin
========

The Salt Bin project is here to allow for single binary builds of Salt
to be easy to make and distribute. Distributing Python applications is
notoriously difficult, and while there are MANY tools that seek to solve
this problem, they can't do it in a universal way.

How
====

Salt-bin is a collection of requirements and configurations to build
distributions of Salt for specific platforms and use cases.

We use pop's build system, as it is built to handle a superset of the
challenges found in building Salt. So to use salt-bin you call out to
the `pop-build` executable.

The pop build system can also make use of `pyenv` to make the builds
target specific versions of python. This allows us to build Salt with
the same version of Python across MANY platforms, which allows for
more rapid development and platform consistency.

Usage
=====

Install pop-build:

* pip install pop-build

It is a good idea to install pyenv as well, see the pyenv install page:

https://github.com/pyenv/pyenv#installation

Now clone the repo:

* git clone https://github.com/saltstack/salt-bin.git
* cd salt-bin

Inside the repo you will find a collection of requirements files and configs.
The configuration files are for pop-build and can be found in the conf directory.

Inside this directory you can make a "basic" build of salt by just calling

* pop-build -c conf/basic.conf

If you have pyenv installed, you can build your binary against a specific version
of Python. Just add the `pyenv` option:

* pop-build -c conf/basic.conf --pyenv 3.7.6

To see the available python versions you can build against run:

* pyenv install --list | grep " 3\.[6789]"

Extending Salt-Bin
==================

Salt-bin is not a python project, it is a collection of configurations used to
make different builds of `Salt` depending on platform and intended use. Salt
does not require that all imaginable deps are included, so salt-bin comes with
configs to install for specific needs and targets.

Salt-bin is extended by adding more build configs for specific platforms. Since
salt-bin is just a collection of `pop-build` configs, you just need to add more
`pop-build` configs.

Add a config file in the conf directory and a requirements.txt file, along with
any other needed files. Take a look at conf/base.conf as an example.

Pop-Build Config
================

The `pop-build` config takes a number of options:

name
----

The name value defines the name of the binary to build, in the case of `salt-bin`
this should always be `salt`

run
----

The run option allows for a specific `run.py` file to be used as the entry point. This
makes it easy to have a custom entry point that only exposed specific components of
Salt in the binary.

requirements
------------

The requirements value points to the requirements file to be used to install deps,
`pop-build` relied on pip to gather the deps during the build and reads a standard
python `requirements.txt` file.

exclude
-------

Sometimes it is useful to exclude specific deps, this can be done by adding those
deps into an `exclude.txt` file. This allows you to uninstall python libs from the
binary.

build
-----

Sometimes a separate .so or .dll is needed to support a specific python library and
they are not always installed with the python code installed via pip. To add a
support dynamic library it can be included in the build tool of `pop-build`.

To use this define the `build` option in the config. This option then takes
an arbitrary number of projects to build into the binary. The build section
can build from the sources:

* build:
*   libsodium:
*     make:
*         - wget https://download.libsodium.org/libsodium/releases/LATEST.tar.gz
*         - tar xvf LATEST.tar.gz
*         - cd libsodium-stable && ./configure && make
*     src: libsodium-stable/src/libsodium/.libs/libsodium.so
*     dest: lib/

This example will download the sources to libsodium, untar them, and compile them.
Then from the compiled code the sources can be set, this is either a single file
or a list of files. Finally the `dest` defines the directory within the binary's
environment where to save the needed artifacts.
