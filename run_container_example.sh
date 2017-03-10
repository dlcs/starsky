#!/bin/bash

docker run \
        --env AWS_ACCESS_KEY_ID="" \
        --env AWS_SECRET_ACCESS_KEY=""  \
	--env STARSKY_ERROR_QUEUE=starsky-error-queue \
	--env STARSKY_TEXT_METADATA_BUCKET=starsky-text-meta \
	--env STARSKY_INDEX_BUCKET=starsky-index \
	--env STARSKY_INGEST_QUEUE=starsky-ingest-queue \
	--env STARSKY_TEXT_QUEUE=starsky-text-queue \
	--env STARSKY_MANIFEST_QUEUE=starsky-manifest-queue \
	--env STARSKY_AWS_REGION=eu-west-1 \
        starsky
