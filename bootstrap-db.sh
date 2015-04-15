#!/bin/bash
ZK=/home/vagrant/zookeeper-3.4.6
ZK_DATA=/home/vagrant/zookeeper-data
sudo apt-get update
sudo apt-get -y install ntp default-jre-headless

# Install zookeeper
tar -xf /vagrant/zookeeper-3.4.6.tar.gz
mkdir -p ${ZK_DATA}
cp -f /vagrant/zoo.cfg ${ZK}/conf/

cat > rc.local <<rc_local_data
#!/bin/bash
${ZK}/bin/zkServer.sh start
rc_local_data
chmod +x rc.local
sudo cp -f rc.local /etc/rc.local

# Install elasticsearch
sudo dpkg -i /vagrant/elasticsearch-1.5.1.deb
sudo update-rc.d elasticsearch defaults 95 10
sudo sed -i "s/#cluster.name:.*$/cluster.name: sync-app/" /etc/elasticsearch/elasticsearch.yml

# NTP
sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart

# System configuration
sudo cp /vagrant/sysctl.conf /etc/
sudo cp /vagrant/limits.conf /etc/security/

