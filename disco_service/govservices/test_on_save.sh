#!/bin/bash
while inotifywait -e close_write govservices/* govservices/management/commands/* ../test_fixtures/*
do
    python manage.py test govservices
done
