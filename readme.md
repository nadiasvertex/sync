The sync app is a prototype distributed application for performing synchronization of complex data items on mobile devices and websites.

# Setup

Run the setup.sh script. This script requires wget. The script will do everything needed to bootstrap the cluster.

## Windows notes

The setup.sh script has also been tested to run under mingw on Windows 8. Note that you must run

```
git config core.autocrlf false
```

for this repo on Windows when checking it out. You must also run your msys shell as an administrator so that vagrant can create the
necessary local network adapters if they don't already exist.

## Optional

If you want to run the application server locally (for development) you must also install pypy, uwsgi, and
kazoo on your local machine. (Pypy is automatically downloaded by the setup script.) Once you have run
the setup script you can:

```
cd $HOME && tar -xf pypy-2.5.1-linux64.tar.bz2
export PATH=$HOME/pypy-2.5.1-linux64/bin:$PATH
pypy get-pip.py
pypy -m pip install uwsgi kazoo
```

# Development

For rapid local testing, run the application server on your dev machine like this:

```
uwsgi --http :9090 --pypy-wsgi app --master --processes 2
```

The client can be run in another terminal:

```
pypy -m client --service=http://localhost:9090 sync-all bookmark
```

This will use the database nodes, but not the web server nodes or load balancer. It is useful for debugging the app.

## Testing the application in distributed mode

Run:

```
./update-web.sh
```

This will copy the local app server code to the web server nodes and restart their uwsgi services. Running the client
in default mode will hit the full cluster:

```
pypy -m client sync-all bookmark
```

# Test framework

There is a simple test framework which exercises the local and remote annotation code. You
can run this by using python:

```
python -m test
```

## Windows notes

If you don't have Python 2.7 installed, you'll need that. Note that the latest
version of python 2.7 (2.7.9) has a version of sqlite3 that doesn't support
full-text search. In order to fix that, you must download the 32-bit Python 2.7
distro, or the 32-bit PyPy 2.7 equivalent (pypy-2.5.x). http://pypy.org/download.html#default-with-a-jit-compiler

Then you have to download the latest sqlite3 .dll for Windows from https://www.sqlite.org/download.html
and replace the sqlite3.dll in the folder with the one you downloaded. 
