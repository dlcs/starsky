#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

COMMAND=$1

if [ "$COMMAND" == "iris" ]; then
	echo Running iris
	python -u iris_listener.py
fi

if [ "$COMMAND" == "ingest-manifest" ]; then
	echo Running ingest-manifest
	python -u starsky_ingest_manifest.py
fi

if [ "$COMMAND" == "ingest" ]; then
	echo Running ingest

	if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
	   aws s3 cp $STARSKY_GOOGLE_CREDENTIALS_S3 $GOOGLE_APPLICATION_CREDENTIALS
	fi

	python -u starsky_ingest.py
fi

if [ "$COMMAND" == "service" ]; then
	echo Running service
	python -u starsky_service.py
fi

