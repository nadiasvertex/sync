#!/bin/bash
sudo apt-get update && sudo apt-get -y dist-upgrade && sudo apt-get -y autoremove
sudo apt-get -y install nginx

sudo cp -f /vagrant/nginx.conf /etc/nginx/sites-available/default
sudo restart nginx
