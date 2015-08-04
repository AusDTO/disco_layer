#!/bin/bash
while inotifywait -e close_write source/*
do
    make clean;
    make html
done
