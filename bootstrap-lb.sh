#!/bin/bash
sudo apt-get update
sudo apt-get -y install ntp nginx

sudo cp -f /vagrant/nginx.conf /etc/nginx/sites-available/default
sudo service nginx restart

sudo cp -f /vagrant/ntp-master.conf /etc/ntp.conf
sudo service ntp restart

sudo cp /vagrant/sysctl.conf /etc/
sudo cp /vagrant/limits.conf /etc/security/
