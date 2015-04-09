#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "2" > ${HOME}/zookeeper-data/myid
${ZK}/bin/zkServer.sh start
