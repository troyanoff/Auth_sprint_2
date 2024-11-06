#!/usr/bin/env bash

while ! nc -z $AUTH_SERVICE_HOST $AUTH_SERVICE_POST; do
      sleep 0.1
done 

pytest src_v1
python3 truncate_tables.py
python3 create_superuser.py
