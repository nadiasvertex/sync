#!/bin/bash
sudo service sync stop
rm -rf /home/vagrant/app
rsync -av --delete --exclude "*.pyc" --exclude "__pycache__" /vagrant/app/ /home/vagrant/app/
