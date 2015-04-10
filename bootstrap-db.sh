#!/bin/bash
CB_CLI=/opt/couchbase/bin/couchbase-cli
sudo dpkg -i /vagrant/couchbase-server-community_3.0.1-ubuntu12.04_amd64.deb

sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart

sudo cp /vagrant/sysctl.conf /etc/
sudo cp /vagrant/limits.conf /etc/security/

