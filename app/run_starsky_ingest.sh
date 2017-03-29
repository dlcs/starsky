#!/bin/bash

if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
   aws s3 cp $STARSKY_GOOGLE_CREDENTIALS_S3 $GOOGLE_APPLICATION_CREDENTIALS
fi

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

touch starsky_ingest.log

python starsky_ingest.py &

tail -f starsky_ingest.log
