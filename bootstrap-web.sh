#!/bin/bash
PYPY=/home/vagrant/pypy-2.5.1-linux64/bin/pypy
UWSGI=/home/vagrant/pypy-2.5.1-linux64/bin/uwsgi
APP=/home/vagrant/app
sudo apt-get update && sudo apt-get -y dist-upgrade && sudo apt-get -y autoremove

# Get pypy
wget https://bitbucket.org/pypy/pypy/downloads/pypy-2.5.1-linux64.tar.bz2
tar -xf pypy-2.5.1-linux64.tar.bz2 && rm pypy-2.5.1-linux64.tar.bz2

# Get pip
wget https://bootstrap.pypa.io/get-pip.py
${PYPY} get-pip.py

# Install/build python modules
${PYPY} -m pip install uwsgi
${PYPY} -m pip install kazoo

mkdir -p ${APP}
find /vagrant/ -name "*.py" | xargs -iTARG ln TARG .

cat > rc.local <<rc_local_data
#!/bin/bash
cd ${APP} && ${UWSGI} --http :9090 --pypy-wsgi app --master --processes 2 --stats :9191
rc_local_data
chmod +x rc.local
sudo cp rc.local /etc/rc.local
