#!/bin/bash
PYPY=/home/vagrant/pypy-2.5.1-linux64/bin/pypy
UWSGI=/home/vagrant/pypy-2.5.1-linux64/bin/uwsgi
APP=/home/vagrant/app
sudo apt-get update
sudo apt-get install -y ntp

# Install pypy
tar -xf /vagrant/pypy-2.5.1-linux64.tar.bz2

# Install pip
${PYPY} /vagrant/get-pip.py

# Install/build python modules
${PYPY} -m pip install uwsgi
${PYPY} -m pip install kazoo
${PYPY} -m pip install elasticsearch

sudo cp /vagrant/web.upstart.config /etc/init/sync.conf

sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart

sudo cp /vagrant/sysctl.conf /etc/
sudo cp /vagrant/limits.conf /etc/security/
