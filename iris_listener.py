from iris_client import IrisListener, IrisClient
import boto3
import settings
import json

iris = IrisClient()
sqs = boto3.resource('sqs', settings.REGION)
queue = sqs.get_queue_by_name(QueueName=settings.MANIFEST_QUEUE)


def handle_manifest(message):

    if message['message_type'] == 'Destiny_Manifest_Added':
        ingest_message = {
            'manifestURI': message.get('manifest_id'),
            'session': message.get('session')
        }
        response = queue.send_message(MessageBody=json.dumps(ingest_message))
        # TODO : log:
        #  "Response status: %s" % (response['ResponseMetadata']['HTTPStatusCode'],)


listener = IrisListener()
listener.run(handle_manifest, "Destiny_Manifest_Added")
