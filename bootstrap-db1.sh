#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "1" > ${ZK_DATA}/myid
sudo ${ZK}/bin/zkServer.sh start
