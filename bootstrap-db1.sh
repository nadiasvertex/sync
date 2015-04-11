#!/bin/bash
. /vagrant/bootstrap-db.sh
sleep 30s
${CB_CLI} cluster-init                       \
       --cluster-username=admin              \
       --cluster-password=letmein            \
       --cluster-port=8091                   \
       --cluster-ramsize=256                 \
       -c 192.168.33.10:8091                 \
       -u Administrator                      \
       -p password

${CB_CLI} bucket-create                      \
       --bucket=sync-app                     \
       --bucket-type=couchbase               \
       --bucket-ramsize=256                  \
       --wait                                \
       -c 192.168.33.10:8091                 \
       -u admin                              \
       -p letmein

