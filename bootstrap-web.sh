#!/bin/bash
PYPY=/home/vagrant/pypy-2.5.1-linux64/bin/pypy
UWSGI=/home/vagrant/pypy-2.5.1-linux64/bin/uwsgi
APP=/home/vagrant/app
sudo apt-get update
sudo apt-get install -y ntp

# Get pypy
wget -c -nv https://bitbucket.org/pypy/pypy/downloads/pypy-2.5.1-linux64.tar.bz2
tar -xf pypy-2.5.1-linux64.tar.bz2

# Get pip
wget -c -nv https://bootstrap.pypa.io/get-pip.py
${PYPY} get-pip.py

# Install/build python modules
${PYPY} -m pip install uwsgi
${PYPY} -m pip install kazoo

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
cd ${APP} && ${UWSGI} --http :80 --pypy-wsgi app --master --processes 2 --stats :9191 --daemonize /var/log/app.log
rc_local_data
chmod +x rc.local
sudo cp rc.local /etc/rc.local

sudo bash rc.local

sudo cp /vagrant/ntp-slave.conf /etc/ntp.conf
sudo service ntp restart
