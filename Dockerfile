FROM centos:6

WORKDIR /opt
COPY . /opt
RUN bash /opt/scripts/cent6_setup.sh
RUN LD_LIBRARY_PATH=/usr/local/python37/lib/:/usr/local/openssl11/lib/ python3.7 /opt/build.py
COPY /opt/dist .
