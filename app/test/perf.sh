#!/bin/bash
httperf --server=localhost --port=8080 --uri=http://localhost:8080/bookmark/uid:10001/cl:E --num-conn=10000 --ra=1000
