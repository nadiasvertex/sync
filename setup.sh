#!/bin/bash
wget -c http://mirror.cc.columbia.edu/pub/software/apache/zookeeper/stable/zookeeper-3.4.6.tar.gz
wget -c https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.1.deb
wget -c https://bitbucket.org/pypy/pypy/downloads/pypy-2.5.1-linux64.tar.bz2
wget -c https://bootstrap.pypa.io/get-pip.py

# Create the cluster
vagrant up

# Update the web app on the web servers
./update-web.sh

# We have to reboot the whole cluster in order to get some configuration changes to take effect.
vagrant reload
