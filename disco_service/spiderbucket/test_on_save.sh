#!/bin/bash
#
# from the parent directory (where manage.py exsts),
# run spiderbucket/test_on_save.sh
#
while inotifywait -e close_write spiderbucket/*
do
    python manage.py test spiderbucket
done
