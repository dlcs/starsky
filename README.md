# Starsky

This is an OCR server and processor for the DLCS. It relies on various AWS features - S3, SQS - so therefore you will need access to an AWS account. For more information on the DLCS see http://dlcs.info

## Sub-components

- starsky_ingest_mainifest.py - SQS listener for manifest level ingest
- starsky_ingest.py - SQS listener for image lvel ingest
- starsky_service.py - HTTP services
- iris_listener.py - listens for incoming "Destiny_Manifest_Added" messages from Iris, indicating that new manfiests are available for procesing in the text pipeline. 

# Operation

Usually Starsky is fed by the iris_listener.py listener which recieves the Iris event stream via its queue (defined by the IRIS_QUEUE environment variable) and for any "Destiny_Manifest_Added" events it adds a message on the manifest ingest queue described below. However content may be added to starsky via one of several other entry points all based upon SQS queues. The simplest is to send a message such as the following to the queue configured with STARSKY_MANIFEST_QUEUE. 

```
{
    "manifestURI": "http://wellcomelibrary.org/iiif/b18035723/manifest",
    "session": "3b5bbe9c-ac37-4ada-8f3e-5fe256f0f792"
}
```

This will be picked up by starsky_ingest_manifest.py. The manifest URI should be any valid IIIF manifest and the session should be a uuid and is passed through stages of the pipeline so that events resultiing from the same originating event can be traced.  This will create a message such as:

```
{
    "imageURI": "https://wellcomelibrary.org/iiif/b18035723/imageanno/ff2085d5-a9c7-412e-9dbe-dda87712228d",
    "metadataURI": "https://wellcomelibrary.org/service/alto/b18035723/0?image=0",
    "session": "3b5bbe9c-ac37-4ada-8f3e-5fe256f0f792"
}
```
one for the first image on each canvas of the first sequence. These messages are placed in the queue defined by STARSKY_INGEST_QUEUE . starsky_ingest.py picks up these messages and follows the ingest procedure described .

# Starsky services

### Plaintext

Gets plaintext for the image URI supplied

method : GET 
example:
```/plaintext/?imageURI=https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500```

returns:

```
{
    "https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500": " 2'38 REVIEW orr vnsr-zs's Tirex'rrse tion\" of which should be \" counteracted we ask again, how is the object of the institution to be accomplished, or what is to become ofthe poor pupil .' Either Mr. Coleman is, or is not capable of teachingr phy- siology and the treatment of disease. About this, although he mayunot have kept l'ull pace with the advance of Veterinary science, and althou'rh he may push some of his l'uVourite theories to an absurd and [ludicro..."
}
```

### Plaintext lines

Where possible this splits the plaintext representation into separate lines.


### Coordinates

Gets the coordinates of bounding boxes around phrases, typically used to avoid storing bounding boxes for every word in a search service, instead just storing the position of the first character. The input requires the uri of the image as well as the character positions of the first character of each token in the phrase which were stored when they were indexed.  The returned result may contain more than one phrase (and hence bounding boxes) if the positions supplied overlap more than one line.

method: POST
example request:
```
{
  "images": [
    {
      "imageURI": "https://dlcs.io/iiif-img/50/1/9a6d377f-5403-4e15-93e2-e2ffa6213f17",
      "width": "1024",
      "positions": [
        [
          "64",
          "68",
          "72",
          "77"
        ]
      ],
      "height": "768"
    }
  ]
}
```

example response:

```
{
  "images": [
    {
      "image_uri": "https://dlcs.io/iiif-img/50/1/9a6d377f-5403-4e15-93e2-e2ffa6213f17",
      "phrases": [
        [
          {
            "count": 2,
            "xywh": "881,98,87,8"
          },
          {
            "count": 2,
            "xywh": "253,115,186,9"
          }
        ]
      ]
    }
  ]
}
```

# Using with Docker

## Docker - installation

```
git clone https://github.com/dlcs/starsky
cd starsky
sudo docker build -t starsky .
```

## AWS CREDENTIALS NOTE
AWS credential environment variables are not required if running as an ECS Task or IAM user/role with permissions for the SQS queues and S3 buckets referenced.

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
	./starsky.sh ingest
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
	./starsky.sh ingest-manifest
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
	./starsky.sh service
```

This will listen on port 5000 by default. Add ```-p=<external-port>:5000``` to the Docker run options to map to a different local port.

# Using without Docker

The python code is contained in the ```app``` folder.

To install dependencies:
```
pip install Cython
pip install -r requirements.txt
```

This is unusual, usually the Cython requirement would be in the requirements.txt file, but due to the parallel calls that pip install makes, the installation fails.

## Running the ingest process
```
./starsky.sh ingest
```

## Running the service process
```
./starsky.sh service
```

