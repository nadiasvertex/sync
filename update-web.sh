#!/bin/bash
for WEB in web1 web2 web3; do
    vagrant ssh ${WEB} -c "bash /vagrant/update-web-stage-2.sh"
    vagrant reload ${WEB}
done
