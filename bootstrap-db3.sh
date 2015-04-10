#!/bin/bash
. /vagrant/bootstrap-db.sh
sleep 30s
${CB_CLI} rebalance -c 192.168.33.10:8091 -u admin -p letmein  \
       --server-add=192.168.33.12:8091                \
       --server-add-username=Administrator            \
       --server-add-password=password
sudo reboot
