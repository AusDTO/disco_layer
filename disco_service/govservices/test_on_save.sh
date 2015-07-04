#!/bin/bash
while inotifywait -e close_write govservices/* govservices/management/* govservices/management/commands/* test_fixtures/*
do
    python manage.py test govservices --failfast -d
done
