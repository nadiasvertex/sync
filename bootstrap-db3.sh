#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "3" > ${HOME}/zookeeper-data/myid
${ZK}/bin/zkServer.sh start
