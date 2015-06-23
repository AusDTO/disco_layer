#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
mkdir ./logs
touch ./logs/access.log
touch ./logs/gunicorn.log
tail -n 0 -f ./logs/*.log &

exec python manage.py \
    celery worker \
    -l info \
    "$@"
