#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "3" > ${ZK_DATA}/myid
sudo ${ZK}/bin/zkServer.sh start
