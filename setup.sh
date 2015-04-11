#!/bin/bash
wget -c http://packages.couchbase.com/releases/3.0.1/couchbase-server-community_3.0.1-ubuntu12.04_amd64.deb
wget -c https://bootstrap.pypa.io/get-pip.py
wget -c http://packages.couchbase.com/ubuntu/couchbase.key

# Create the cluster
vagrant up

# Update the web app on the web servers
./update-web.sh

# We have to reboot the whole cluster in order to get some configuration changes to take effect.
vagrant reload
