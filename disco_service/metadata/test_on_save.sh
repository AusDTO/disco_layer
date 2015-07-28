#!/bin/bash
#
# from the parent directory (where manage.py exsts),
# run metadata/test_on_save.sh
#
while inotifywait -e close_write metadata/*
do
    python manage.py test metadata
done
