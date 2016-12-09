#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
python starsky_ingest.py &
python starsky_service.py &
while true; do sleep 10; done