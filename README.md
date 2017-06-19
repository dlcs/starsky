# Starsky

This is an OCR server and processor for the DLCS. It relies on various AWS features - S3, SQS - so therefore you will need access to an AWS account. For more information on the DLCS see http://dlcs.info

## Sub-components

- starsky_inget_mainifest.py - SQS listener for manifest level ingest
- starsky_ingest.py - SQS listener for image lvel ingest
- starsky_serice.py - HTTP services
- iris_listener.py - listens for incoming "Destiny_Manifest_Added" messages from Iris, indicating that new manfiests are available for procesing in the text pipeline. 

# Operation

Usually Starsky is fed by the iris_listener.py listener which recieves the Iris event stream via its queue (defined by the IRIS_QUEUE environment variable) and for any "Destiny_Manifest_Added" events it adds a message on the manifest ingest queue described below. However content may be added to starsky via one of several other entry points all based upon SQS queues. The simplest is to send a message such as:

```
{
    "manifestURI": "http://wellcomelibrary.org/iiif/b18035723/manifest",
    "session": "3b5bbe9c-ac37-4ada-8f3e-5fe256f0f792"
}
```

to the queue configured with STARSKY_MANIFEST_QUEUE. This will be picked up by starsky_ingest_manifest.py. The manifest URI should be any valid IIIF manifest and the session should be a uuid and is passed through stages of the pipeline so that events resultiing from the same originating event can be traced.  This will create a message such as:

```
{
    "imageURI": "https://wellcomelibrary.org/iiif/b18035723/imageanno/ff2085d5-a9c7-412e-9dbe-dda87712228d",
    "metadataURI": "https://wellcomelibrary.org/service/alto/b18035723/0?image=0",
    "session": "3b5bbe9c-ac37-4ada-8f3e-5fe256f0f792"
}
```
one for the first image on each canvas of the first sequence. These messages are placed in the queue defined by STARSKY_INGEST_QUEUE . starsky_ingest.py picks up these messages and follows the ingest procedure described .

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

