#!/bin/bash
#
# if DISCO_ROLE==WORKER, then run as a celery node
# otherwise run as a front-end node
#
LOGLEVEL=info

python manage.py migrate
python manage.py collectstatic --noinput
mkdir ./logs
touch ./logs/access.log
touch ./logs/gunicorn.log
tail -n 0 -f ./logs/*.log &

if [ "$DISCO_ROLE" == "WORKER" ]
then
    exec python manage.py celery worker -l info "$@"
elif [ "$DISCO_ROLE" == "BEAT" ]
then
    exec python manage.py celery beat -l info "$@" 
else
    exec gunicorn disco_service.wsgi:application \
	--name disco_service \
	--bind 0.0.0.0:8000 \
	--workers 3 \
	--log-level=$LOGLEVEL \
	--log-file=./logs/gunicorn.log \
	--access-logfile=./logs/access.log \
	"$@"
fi
