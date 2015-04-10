#!/bin/bash
httperf --hog --uri=http://localhost:8080/bookmark/uid:10001/cl:E --num-conn 1000 --ra 100
