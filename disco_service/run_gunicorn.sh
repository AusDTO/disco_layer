#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput

mkdir ./logs
touch ./logs/access.log
touch ./logs/gunicorn.log
tail -n 0 -f ./logs/*.log &

exec gunicorn disco_service.wsgi:application \
    --name disco_service \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/access.log \
    "$@"

