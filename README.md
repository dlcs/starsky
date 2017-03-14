# Starsky

This is an OCR server and processor. It relies on various AWS features - S3, SQS - so therefore you will need access to an AWS account.

# Using with Docker

## Docker - installation

```
git clone https://github.com/dlcs/starsky
cd starsky
sudo docker build -t starsky .
```

## Docker - Running the ingest process
```
sudo docker run -d --name starsky-ingest \
	--env AWS_ACCESS_KEY_ID="<access-key>" \
        --env AWS_SECRET_ACCESS_KEY="<secret-key>"  \
	--env STARSKY_ERROR_QUEUE=<error-queue-name> \
	--env STARSKY_TEXT_METADATA_BUCKET=<text-metadata-bucket> \
	--env STARSKY_INDEX_BUCKET=<index-bucket-name> \
	--env STARSKY_INGEST_QUEUE=<ingest-queue-name> \
	--env STARSKY_TEXT_QUEUE=<text-queue-name> \
	--env STARSKY_MANIFEST_QUEUE=<manifest-queue-name> \
	--env STARSKY_AWS_REGION=<aws-region> \
	starsky \
	./run_starsky_ingest.sh
```

## Docker - Running the ingest-manifest process
```
sudo docker run -d --name starsky-ingest-manifest \
	--env AWS_ACCESS_KEY_ID="<access-key>" \
        --env AWS_SECRET_ACCESS_KEY="<secret-key>"  \
	--env STARSKY_ERROR_QUEUE=<error-queue-name> \
	--env STARSKY_TEXT_METADATA_BUCKET=<text-metadata-bucket> \
	--env STARSKY_INDEX_BUCKET=<index-bucket-name> \
	--env STARSKY_INGEST_QUEUE=<ingest-queue-name> \
	--env STARSKY_TEXT_QUEUE=<text-queue-name> \
	--env STARSKY_MANIFEST_QUEUE=<manifest-queue-name> \
	--env STARSKY_AWS_REGION=<aws-region> \
	starsky \
	./run_starsky_ingest_manifest.sh
```

This will listen on port 5000 by default. Add ```-p=<external-port>:5000``` to the Docker run options to map to a different local port.

## Docker - Running the service process
```
sudo docker run -d --name starsky-service \
	--env AWS_ACCESS_KEY_ID="<access-key>" \
        --env AWS_SECRET_ACCESS_KEY="<secret-key>"  \
	--env STARSKY_ERROR_QUEUE=<error-queue-name> \
	--env STARSKY_TEXT_METADATA_BUCKET=<text-metadata-bucket> \
	--env STARSKY_INDEX_BUCKET=<index-bucket-name> \
	--env STARSKY_INGEST_QUEUE=<ingest-queue-name> \
	--env STARSKY_TEXT_QUEUE=<text-queue-name> \
	--env STARSKY_MANIFEST_QUEUE=<manifest-queue-name> \
	--env STARSKY_AWS_REGION=<aws-region> \
	starsky \
	./run_starsky_service.sh
```

This will listen on port 5000 by default. Add ```-p=<external-port>:5000``` to the Docker run options to map to a different local port.

# Using without Docker

The python code is contained in the ```app``` folder.

To install dependencies:
```
pip install Cython
pip install -r requirements.txt
```

This in unusual, usually the Cython requirement would be in the requirements.txt file, but due to the parallel calls that pip install makes, the installation fails.

## Running the ingest process
```
./run_starsky_ingest.sh
```

## Running the service process
```
./run_starsky_service.sh
```

