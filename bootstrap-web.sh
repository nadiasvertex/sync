#!/bin/bash
PY=/usr/bin/python2
UWSGI=/usr/local/bin/uwsgi
APP=/home/vagrant/app

sudo apt-key add /vagrant/couchbase.key
sudo cp -f /vagrant/couchbase.list /etc/apt/sources.list.d/

sudo apt-get update
sudo apt-get install -y ntp libcouchbase2-core libcouchbase-dev python-dev

# Install pip
sudo ${PY} /vagrant/get-pip.py

# Install/build python modules
sudo ${PY} -m pip install uwsgi
sudo ${PY} -m pip install couchbase

if [ -d "${APP}" ]; then
    if [ ! -L "${APP}" ]; then
        rm -rf ${APP}
    fi
fi

if [ ! -d "${APP}" ]; then
    ln -s /vagrant/app ${APP}
fi

cat > rc.local <<rc_local_data
#!/bin/bash
cd ${APP} && ${UWSGI} --http :80 --wsgi-file app.py --master --processes 2 --stats :9191 --daemonize /var/log/app.log
rc_local_data
chmod +x rc.local
sudo cp rc.local /etc/rc.local

sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart

sudo cp /vagrant/sysctl.conf /etc/
sudo cp /vagrant/limits.conf /etc/security/
sudo reboot
