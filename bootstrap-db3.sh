#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "3" > ${ZK_DATA}/myid
sudo reboot
