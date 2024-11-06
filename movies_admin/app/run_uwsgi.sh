#!/usr/bin/env bash

while ! nc -z $POSTGRES_HOST $PGPORT; do
      sleep 0.1
done 

set -e

chown www-data:www-data /var/log


python3 /opt/app/manage.py collectstatic --noinput
python3 /opt/app/manage.py migrate --fake movies
python3 /opt/app/manage.py migrate
python3 /opt/app/manage.py compilemessages -l en -l ru 
python3 /opt/app/manage.py createsuperuser --noinput || true 

uwsgi --strict --ini /opt/app/uwsgi.ini
