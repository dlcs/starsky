#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

touch iris.log

python iris_listener.py &

tail -f iris.log
