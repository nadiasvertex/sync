#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "1" > ${ZK_DATA}/myid
