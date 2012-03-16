#!/bin/sh


sqlite3 /var/www/wedding/data/weddingdata.sqlite .dump  > /var/www/wedding/djwed/data/weddingdata-backup.dump
#sqlite3 /var/www/wedding/data/weddingdata.sqlite ".backup /var/www/wedding/djwed/data/weddingdata-backup.sqlite"
cd /var/www/wedding/djwed/data/
svn commit weddingdata-backup.dump -m "regular database backup"

