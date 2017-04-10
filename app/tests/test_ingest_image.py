import unittest
import starsky_ingest
import json
import boto3
import settings
import iris_settings
import boto

from moto import mock_sqs, mock_s3, mock_sns

@mock_sqs
@mock_s3
@mock_sns
class TestIngest(unittest.TestCase):

    def test_process_message(self):

        # creating some mock sqs resources. We won't use them here but it means the initialisation will succeed
        sqs = boto3.resource('sqs')
        sqs.create_queue(QueueName=settings.INGEST_QUEUE)
        sqs.create_queue(QueueName=settings.TEXT_QUEUE)
        sqs.create_queue(QueueName=settings.ERROR_QUEUE)
        sqs.create_queue(QueueName=iris_settings.IRIS_SQS_APP_QUEUE)
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=settings.INDEX_BUCKET)
        s3.create_bucket(Bucket=settings.TEXT_METADATA_BUCKET)
        sns = boto3.resource('sns')
        sns.create_topic(Name=iris_settings.IRIS_SNS_TOPIC)

        message = Message()
        message.body = json.dumps(
            {
                "images":
                [
                    {"imageURI": "http://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500"}
                ]
            })
        s = starsky_ingest.Starsky()
        s.init()
        s.process_message(message)


class Message:

    def __init__(self):
        self.message = ""
