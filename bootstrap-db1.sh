#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "1" > ${HOME}/zookeeper-data/myid
${ZK}/bin/zkServer.sh start
