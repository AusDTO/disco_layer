#!/bin/bash
while inotifywait -e close_write spiderbucket/*
do
    python manage.py test
done
