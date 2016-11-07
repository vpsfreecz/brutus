#!/usr/bin/env bash

FAILED=0

nosetests || ((FAILED++))

sudo /etc/init.d/apache2 stop
sudo /etc/init.d/nginx stop

if [ "$SKIP_DEPLOY" == "" ]; then
    sudo ./brutus-deploy --srcdir=tmp/output / || ((FAILED++))
fi

if [ "$SERVER" == "nginx" ]; then
    sudo useradd --no-create-home nginx
    sudo nginx -t || ((FAILED++))
    sudo /etc/init.d/nginx start || ((FAILED++))
fi

if [ "$SERVER" == "apache" ]; then
    sudo /etc/init.d/apache2 start || ((FAILED++))
fi

curl http://127.0.0.1/ || ((FAILED++))

echo "Failed tests: $FAILED"
exit $FAILED
