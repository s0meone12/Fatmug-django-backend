#!/bin/sh
echo "Pre script running"
python /app/manage.py makemigrations
python /app/manage.py makemigrations core
python /app/manage.py migrate