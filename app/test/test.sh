#!/bin/bash
printf "`curl --silent --upload-file b1.json http://localhost:8080/bookmark/uid:10001/cl:E`\n"
printf "`curl --silent --upload-file b2.json http://localhost:8080/bookmark/uid:10001/cl:E`\n"
printf "`curl --silent --upload-file b3.json http://localhost:8080/bookmark/uid:10001/cl:E`\n"
printf "`curl --silent --upload-file b4.json http://localhost:8080/bookmark/uid:10001/cl:E`\n"
