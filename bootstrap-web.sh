#!/bin/bash
PY=/usr/bin/python2
UWSGI=/usr/local/bin/uwsgi
APP=/home/vagrant/app

sudo apt-key add /vagrant/couchbase.key
sudo cp -f /vagrant/couchbase.list /etc/apt/sources.list.d/

sudo apt-get update
sudo apt-get install -y ntp libcouchbase2-core libcouchbase-dev python-dev

# Install pip
sudo ${PY} /vagrant/get-pip.py

# Install/build python modules
sudo ${PY} -m pip install uwsgi
sudo ${PY} -m pip install couchbase

sudo cp /vagrant/web.upstart.config /etc/init/sync.conf

sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart

sudo cp /vagrant/sysctl.conf /etc/
sudo cp /vagrant/limits.conf /etc/security/
