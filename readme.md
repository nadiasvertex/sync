The sync app is a prototype distributed application for performing synchronization of complex data items on mobile devices and websites.

# Setup

Run the setup.sh script. This script requires wget. The script will do everything needed to bootstrap the cluster.

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

