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

We use pop's build system, as it is build top handle a superset of the
challanges found in building Salt. So to use salt-bin you call out to
the `pop-build` executable.

The pop build system can also make use of `pyenv` to make the builds
target specific versions of python. This allows us to build Salt with
the same version of Python accross MANY platforms, which allows for
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

Inside the repo you will find a collection of requirements files and a `run.py`.

Inside this directory you can make a "basic" build of salt by just calling
`pop-build -n salt`.


