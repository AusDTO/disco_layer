#!/bin/bash
for x in `cat ../ops/alpha_disco/disco_service.env`; do export $x; done
