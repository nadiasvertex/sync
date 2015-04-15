#!/bin/bash
. /vagrant/bootstrap-db.sh
echo "3" > ${ZK_DATA}/myid
sudo sed -i "s/#node.name:.*$/node.name: db3/" /etc/elasticsearch/elasticsearch.yml
sudo sed -i "s/#network.publish_host:.*$/network.publish_host: 192.168.33.12/" /etc/elasticsearch/elasticsearch.yml
