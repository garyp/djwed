#!/bin/sh

cd /var/www/wedding/djwed/

echo Backing up production database
sqlite3 /var/www/wedding/data/weddingdata.sqlite ".backup data/weddingdata-prod.sqlite"
svn commit data/weddingdata-prod.sqlite -m "copy production db prior to sync"

echo Syncing out updates
svn update
touch django.wsgi
sudo /usr/sbin/apache2ctl restart
sleep 2
echo Done...  Now go test the live site at http://wedding.example.org/




