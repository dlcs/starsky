# Starsky

## Installation

```
git clone https://github.com/john-root/starsky
cd starsky
sudo docker build -t starsky .
```

## Running - ingest
```
sudo docker run -d --name starsky-ingest \
	--env AWS_ACCESS_KEY_ID="<access-key>" \
        --env AWS_SECRET_ACCESS_KEY="<secret-key>"  \
	--env STARSKY_ERROR_QUEUE=<error-queue-name> \
	--env STARSKY_TEXT_METADATA_BUCKET=<text-metadata-bucket> \
	--env STARSKY_INDEX_BUCKET=<index-bucket-name> \
	--env STARSKY_INGEST_QUEUE=<ingest-queue-name> \
	--env STARSKY_AWS_REGION=<aws-region> \
	starsky \
	./run_starsky_ingest.sh
```

## Running - service
```
sudo docker run -d --name starsky-service \
	--env AWS_ACCESS_KEY_ID="<access-key>" \
        --env AWS_SECRET_ACCESS_KEY="<secret-key>"  \
	--env STARSKY_ERROR_QUEUE=<error-queue-name> \
	--env STARSKY_TEXT_METADATA_BUCKET=<text-metadata-bucket> \
	--env STARSKY_INDEX_BUCKET=<index-bucket-name> \
	--env STARSKY_INGEST_QUEUE=<ingest-queue-name> \
	--env STARSKY_AWS_REGION=<aws-region> \
	starsky \
	./run_starsky_service.sh
```

