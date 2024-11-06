#!/usr/bin/env bash

while ! nc -z $POSTGRES_HOST $PGPORT; do
      sleep 0.1
done 

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 200