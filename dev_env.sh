#!/bin/bash
for x in `cat ../ops/alpha_disco/disco_service.env`; do export $x; done
# assumes you have done `virtualenv .venv`
# then `pip install -r requirements`
. .venv/bin/activate
