#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

touch starsky_service.log

python starsky_service.py &

tail -f starsky_service.log

