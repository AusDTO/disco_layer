#!/bin/bash
# cheaky way to get deps setup on a host, e.g. dev machine
cat Dockerfile | grep RUN | grep apt-get | grep install | sed -s 's/RUN apt-get install -y//g' | xargs sudo apt-get install -y
