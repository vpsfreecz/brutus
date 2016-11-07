#!/usr/bin/env bash

FAILED=0

if [ "$DESTDIR" == "" ]; then
    DESTDIR=/
fi

nosetests || ((FAILED++))

sudo /etc/init.d/apache2 stop
sudo /etc/init.d/nginx stop

if [ "$SKIP_DEPLOY" == "" ]; then
    sudo ./brutus-deploy --srcdir=tmp/output $DESTDIR || ((FAILED++))
    sudo ./brutus-deploy --srcdir=tests/root $DESTDIR || ((FAILED++))
fi

if [ "$SERVER" == "nginx" ]; then
    sudo useradd --no-create-home nginx
    sudo nginx -t || ((FAILED++))
    sudo /etc/init.d/nginx start || ((FAILED++))
fi

if [ "$SERVER" == "apache" ]; then
    sudo /etc/init.d/apache2 start || ((FAILED++))
fi

echo "Testing example.net"
curl -v http://example.net/ || ((FAILED++))
echo "Testing mini.example.net"
curl -v http://mini.example.net/ || ((FAILED++))

echo "Failed tests: $FAILED"
exit $FAILED
