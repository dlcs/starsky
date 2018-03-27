import requests
import json
import boto3
import sys

import settings
import os
import logging
import aws


def main():

    ingest = IngestManifest()
    ingest.init()
    if len(sys.argv) == 2:
        ingest.ingest_manifest(sys.argv[1])
    else:
        ingest.run()


class IngestManifest:

    def __init__(self):

        # defer AWS initialisation to init() method to allow simpler instantiation for testing
        self.sqs = None
        self.s3 = None
        self.starsky_ingest_queue = None
        self.error_queue = None
        self.manifest_queue = None

    def init(self):

        self.set_logging()
        self.sqs = aws.get_sqs_resource()
        self.manifest_queue = aws.get_queue_by_name(self.sqs, settings.MANIFEST_QUEUE)
        self.starsky_ingest_queue = aws.get_queue_by_name(self.sqs, settings.INGEST_QUEUE)
        self.error_queue = aws.get_queue_by_name(self.sqs, settings.ERROR_QUEUE)

    def run(self):

        try:
            while True:
                if os.path.exists('/tmp/stop.txt'):
                    sys.exit()
                messages = aws.get_messages_from_queue(self.manifest_queue)
                for message in messages:
                    if message is not None:
                        try:
                            self.process_message(message)
                        except:
                            logging.exception("Error processing message")
                            aws.send_message(self.error_queue, message.body)
                        finally:
                            message.delete()
        except Exception as e:
            logging.exception("Error getting messages")

    def process_message(self, message):

        message_data = json.loads(message.body)
        manifest_uri = message_data.get("manifestURI")
        session = message_data.get("session")
        if manifest_uri is not None:
            self.ingest_manifest(manifest_uri, session)
        else:
            logging.error("No manifest URI found")

    def ingest_manifest(self, manifest_uri, session=None):

        image_uris = []

        response = requests.get(manifest_uri)

        if response.status_code == 200:

            manifest = json.loads(response.text)

            for canvas in manifest["sequences"][0]["canvases"]:

                # assume first image annotating canvas is the one we want
                first_image = canvas["images"][0]
                if first_image is not None:

                    image_uri = first_image["resource"]["service"]["@id"]
                    # TODO check for alto or hocr

                    image = {"imageURI": image_uri}

                    service_type, service_uri = self.get_text_service(canvas)
                    if service_type is not None and service_type in ['hocr', 'alto'] and service_uri is not None:
                        image['metadataURI'] = service_uri
                    if session is not None:
                        image['session'] = session

                    image_uris.append(image)

            message = {"images": image_uris}

            sqs = boto3.resource('sqs', settings.REGION)
            queue = sqs.get_queue_by_name(QueueName=settings.INGEST_QUEUE)
            queue.send_message(MessageBody=json.dumps(message))

        else:
            print("Error retriving manifest")

    def get_text_service(self, canvas):

        try:
            if isinstance(canvas['seeAlso'], list):
                for see_also in canvas['seeAlso']:
                    service_type, service_uri = self.identify_see_also(see_also)
                    if service_type is not None:
                        return service_type, service_uri
            else:
                return self.identify_see_also(canvas['seeAlso'])
        except KeyError:
            return None, None


    def identify_see_also(self, see_also):

        if 'alto' in see_also['profile'].lower():
            return 'alto', see_also['@id']
        elif 'hocr' in see_also['profile'].lower():
            return 'hocr', see_also['@id']
        else:
            return None, None

    @staticmethod
    def set_logging():

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', )
        logging.getLogger('boto3').setLevel(logging.ERROR)
        logging.getLogger('botocore').setLevel(logging.ERROR)
        logging.getLogger('werkzeug').setLevel(logging.ERROR)


if __name__ == "__main__":
    main()
