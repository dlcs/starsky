import boto3
import settings
import logging


def delete_s3_object(s3, bucket, key):

    logging.debug("Attempting to delete key %s from bucket %s" % (key, bucket))
    s3.meta.client.delete_object(Bucket=bucket, Key=key)


def move_s3_object(s3, bucket, old, new):

    logging.debug("Attempting to move key %s to key %s in bucket %s" % (old, new, bucket))
    s3.meta.client.copy_object(CopySource={'Bucket': bucket, 'Key': old}, Bucket=bucket, Key=new)
    s3.meta.client.delete_object(Bucket=bucket, Key=old)


def put_s3_object(s3, bucket, key, data):

    s3.meta.client.put_object(Bucket=bucket, Key=key, Body=data)


def get_s3_object(s3, bucket, key):

    return s3.meta.client.get_object(Bucket=bucket, Key=key)


def get_queue_by_name(sqs, name):

    return sqs.get_queue_by_name(QueueName=name)


def get_messages_from_queue(queue):

    return queue.receive_messages(WaitTimeSeconds=settings.POLL_INTERVAL)


def send_message(queue, result_string):

    queue.send_message(MessageBody=result_string)


def get_sqs_resource():

    return boto3.resource('sqs', settings.REGION)


def get_transcoder_client():

    return boto3.client('elastictranscoder', settings.REGION)


def get_s3_resource():

    return boto3.resource('s3')