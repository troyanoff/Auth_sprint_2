#!/usr/bin/env bash

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
done 

alembic upgrade head
python3 create_superuser.py

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8200 --timeout 200