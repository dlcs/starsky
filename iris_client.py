import iris_settings
import logging
import boto3
import time
import json
import uuid
from collections import OrderedDict


class IrisClient:

    def __init__(self):

        self.IRIS_POLL_INTERVAL = 20
        self.sns_client = boto3.client('sns', iris_settings.AWS_REGION)
        self.sqs = boto3.resource('sqs', iris_settings.AWS_REGION)
        self.iris_queue = self.sqs.get_queue_by_name(QueueName=iris_settings.IRIS_SQS_APP_QUEUE)
        self.iris_topic = self.sns_client.create_topic(Name=iris_settings.IRIS_SNS_TOPIC).get('TopicArn')

    def get_new_session_id(self):

        return str(uuid.uuid4())

    def send_iris_message(self, message):

        message['timestamp'] = time.time()
        response = self.sns_client.publish(
            TopicArn=self.iris_topic,
            Message=json.dumps(message)
        )

        return response.get('MessageId')

    def read_iris_messages(self, count=5):

        messages = self.iris_queue.receive_messages(WaitTimeSeconds=iris_settings.IRIS_POLL_INTERVAL,
                                                    MaxNumberOfMessages=count)
        unwrapped_messages = []
        for message in messages:
            # unwrap SNS and SQS bodies, get payload
            # add in message id to body
            # return
            unwrapped_message = {'message': json.loads(json.loads(message.body, object_pairs_hook=OrderedDict)
                                                       .get('Message')),
                                 'sqs_message': message}
            unwrapped_message['message']['message_id'] = message.message_id
            unwrapped_messages.append(unwrapped_message)

        return unwrapped_messages


class IrisListener:

    def __init__(self):

        self.set_logging()
        self.iris = IrisClient()
        self.stop = False

    def run(self, callback, message_filter=None):

        try:
            while not self.stop:
                for message in self.iris.read_iris_messages():
                    if message is not None:
                        # noinspection PyBroadException
                        # broad except as no knowledge of callback
                        try:
                            if message_filter is None or len(message_filter) == 0 \
                                    or message['message']['message_type'] \
                                    in message_filter:
                                callback(message['message'])
                        except:
                            logging.exception("Error processing Iris message")
                        finally:
                            message['sqs_message'].delete()

        except Exception as e:
            logging.exception("Error getting Iris messages")
            raise e

    @staticmethod
    def set_logging():

        logging.basicConfig(filename="iris.log",
                            filemode='a',
                            level=logging.DEBUG,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', )
        logging.getLogger('boto').setLevel(logging.ERROR)
        logging.getLogger('botocore').setLevel(logging.ERROR)
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
