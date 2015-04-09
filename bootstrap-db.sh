#!/bin/bash
ZK=/home/vagrant/zookeeper-3.4.6
ZK_DATA=/home/vagrant/zookeeper-data
sudo apt-get update
sudo apt-get -y install ntp default-jre

wget -c -nv http://mirror.cc.columbia.edu/pub/software/apache/zookeeper/stable/zookeeper-3.4.6.tar.gz
tar -xf zookeeper-3.4.6.tar.gz #&& rm zookeeper-3.4.6.tar.gz
mkdir -p ${ZK_DATA}
cp -f /vagrant/zoo.cfg ${ZK}/conf/

cat > rc.local <<rc_local_data
#!/bin/bash
${ZK}/bin/zkServer.sh start
rc_local_data
chmod +x rc.local
sudo cp -f rc.local /etc/rc.local

sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart
