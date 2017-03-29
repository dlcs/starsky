#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

touch starsky_ingest_manifest.log

python starsky_ingest_manifest.py &

tail -f starsky_ingest_manifest.log
