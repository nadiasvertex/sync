#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "2" > ${ZK_DATA}/myid
sudo ${ZK}/bin/zkServer.sh start
