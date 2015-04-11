#!/bin/bash
for WEB in web1 web2 web3; do
    vagrant ssh ${WEB} -c "rsync -av --delete --exclude \"*.pyc\" --exclude __pycache__ /vagrant/app/ /home/vagrant/app/; sudo service sync restart"
done
