import boto3
import settings
import json

message = {
    'images':
        [
            # {
            #     "imageURI": "https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500"
            # },
            # {
            #     "imageURI": "https://dlcs.io/iiif-img/2/1/6b33280a-d28f-4773-be0d-05bd364c745e",
            #     "metadataURI": "http://wellcomelibrary.org/service/alto/b28047345/0?image=47"
            # },
            {
                "imageURI": "https://dlcs.io/iiif-img/2/1/e2616033-5268-4b6f-886f-00a5ab48439c",
                "metadataURI": "http://localhost:8000/ocropus_trained.html"
            }
        ]
}

sqs = boto3.resource('sqs', settings.REGION)
queue = sqs.get_queue_by_name(QueueName=settings.INGEST_QUEUE)
response = queue.send_message(MessageBody=json.dumps(message))
print "Response status: %s" % (response['ResponseMetadata']['HTTPStatusCode'],)
