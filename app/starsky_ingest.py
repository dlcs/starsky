import importlib
import json
import logging
import os
import sys
from urllib import quote_plus

import requests
from bs4 import BeautifulSoup

import aws
import metadata_indexers
import settings
import iris_client


def main():

    starsky = Starsky()
    starsky.init()
    starsky.run()


class Starsky:

    def __init__(self):

        # defer AWS initialisation to init() method to allow simpler instantiation for testing
        self.sqs = None
        self.s3 = None
        self.ingest_queue = None
        self.error_queue = None
        self.text_queue = None
        self.ocr_plugin = importlib.import_module(settings.OCR_PLUGIN)
        self.iris = None

    def init(self):

        self.set_logging()
        self.sqs = aws.get_sqs_resource()
        self.s3 = aws.get_s3_resource()
        self.ingest_queue = aws.get_queue_by_name(self.sqs, settings.INGEST_QUEUE)
        self.error_queue = aws.get_queue_by_name(self.sqs, settings.ERROR_QUEUE)
        self.text_queue = aws.get_queue_by_name(self.sqs, settings.TEXT_QUEUE)
        self.iris = iris_client.IrisClient()

    def run(self):

        try:
            while True:
                if os.path.exists('/tmp/stop.txt'):
                    sys.exit()
                for message in self.get_messages_from_queue():
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

    """
        example message body:
        {
           'images':
            [
                {
                    "imageURI": "<Image_Uri>",
                    "metadataURI": "<alto, hocr, plaintext URI>,
                    "hints": {"orig_dpi": 600}],       # or e.g. "textConfidence": 100
                    "session: "<guid as string>"  (optional)
                }
            ...
            ]
        }
    """
    def process_message(self, message):

        message_data = json.loads(message.body)
        if 'images' not in message_data:
            raise ParseError(message, "images element not found in message body")

        for image in message_data['images']:

            image_uri = image.get("imageURI")
            metadata_uri = image.get("metadataURI")
            ocr_hints = image.get("hints")
            session = image.get("session")

            try:

                # get or generate text metadata
                local_metadata, metadata_format = self.get_metadata(image_uri, metadata_uri, ocr_hints)

                if local_metadata is None:

                    # no metadata supplied and no usable metadata could be generated
                    self.iris.send_iris_message({
                        'message_type': 'Image_Processed',
                        'process': 'starsky',
                        'image_uri': image_uri,
                        'session': session,
                        'flag_no_text': 'true',
                        'resolution': 'success'
                    })
                    continue

                # store metadata in s3
                self.store_metadata(image_uri, local_metadata)

                # obtain width and height of OCRed image from metadata
                ocr_width, ocr_height, canvas_width, canvas_height = self.get_width_height(local_metadata, metadata_format, image_uri)

                # create image data structure for output
                image_data = {
                    'metadata_format': metadata_format,
                }
                if ocr_width is not None and ocr_height is not None:
                    image_data['width'] = ocr_width
                    image_data['height'] = ocr_height
                    image_data['canvas_width'] = canvas_width
                    image_data['canvas_height'] = canvas_height

                # generate indexes and add to image data
                word_index, start_index, confidence = metadata_indexers.get_words(local_metadata, metadata_format)
                image_data['word_index'] = word_index
                image_data['start_index'] = start_index
                image_data['confidence'] = confidence

                # store image data in S3 as json blob
                self.store_json(image_uri, json.dumps(image_data))

                self.iris.send_iris_message({
                    'message_type': 'Image_Processed',
                    'process': 'starsky',
                    'image_uri': image_uri,
                    'session': session,
                    'resolution': 'success'
                })

            except:

                logging.exception("Error getting messages")
                self.iris.send_iris_message({
                    'message_type': 'Image_Processed',
                    'process': 'starsky',
                    'image_uri': image_uri,
                    'session': session,
                    'resolution': 'failure'
                })

    def get_metadata(self, image_uri, metadata_uri, ocr_hints):

        if metadata_uri is not None:
            # we have metadata, lets retrieve it
            metadata = self.get_metadata_from_uri(metadata_uri)
            metadata_format = self.identify_format(metadata)
            return metadata, metadata_format

        else:
            # we don't have any metadata, create it
            metadata, metadata_format = self.ocr_plugin.ocr_image(image_uri, ocr_hints)
            return metadata, metadata_format

    @staticmethod
    def get_width_height(metadata, metadata_format, image_uri):

        # heights and widths are in units native to the format, as output is scaled the unit is irrelevant as
        # long as the word boxes are stored in the same unit

        width = None
        height = None

        # TODO : consider retry?
        response = requests.get(image_uri + "/info.json")
        if response.status_code != 200:
            raise IOError("ImageURI not found")
        else:
            info = json.loads(response.text)
            canvas_width = int(info.get('width'))
            canvas_height = int(info.get('height'))

        if metadata_format == 'alto':
            soup = BeautifulSoup(metadata, "html.parser")
            attributes_dictionary = soup.find('page').attrs
            width = int(attributes_dictionary['width'])
            height = int(attributes_dictionary['height'])

        elif metadata_format == "hocr":
            soup = BeautifulSoup(metadata, "html.parser")
            page_element = soup.find("div", {"class": "ocr_page"})
            title = page_element['title']
            split = title.split(';')
            if len(split) > 1:
                bbox = split[1].split()[1:]
                width = int(bbox[2]) - int(bbox[0])
                height = int(bbox[3]) - int(bbox[1])

        if width is None or height is None:
            width = canvas_width
            height = canvas_height

        return width, height, canvas_width, canvas_height


    @staticmethod
    def identify_format(local_metadata):

        if "<alto " in local_metadata:
            logging.debug("metadata identified as alto")
            return "alto"
        elif "<div class='ocr_page' " in local_metadata:
            logging.debug("metadata identified as hocr")
            return "hocr"
        else:
            logging.debug("assuming metadata is plaintext")
            return "text"

    def get_messages_from_queue(self):

        logging.debug("checking queue for messages")
        messages = aws.get_messages_from_queue(self.ingest_queue)
        return messages

    def store_metadata(self, image_uri, metadata):

        logging.debug("storing metadata in s3 for %s", image_uri)
        encoded_uri = quote_plus(image_uri)
        aws.put_s3_object(self.s3, settings.TEXT_METADATA_BUCKET, encoded_uri, metadata)

    def store_json(self, image_uri, json_data):
        
        logging.debug("storing index data in s3 for %s", image_uri)
        encoded_uri = quote_plus(image_uri)
        aws.put_s3_object(self.s3, settings.INDEX_BUCKET, encoded_uri, json_data)

    @staticmethod
    def get_metadata_from_uri(metadata_uri):

        logging.debug("attempting to download metadata from %s", metadata_uri)
        r = requests.get(metadata_uri)
        if r.status_code != 200:
            # TODO consider retry?
            logging.error("Could not obtain metadata from %s", metadata_uri)
            raise IOError("Error getting metadata from uri {}".format(metadata_uri))
        else:
            return r.text

    @staticmethod
    def set_logging():

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', )
        logging.getLogger('boto3').setLevel(logging.ERROR)
        logging.getLogger('botocore').setLevel(logging.ERROR)
        logging.getLogger('werkzeug').setLevel(logging.ERROR)


class ParseError(RuntimeError):

    def __init__(self, text, msg):

        self.text = text
        self.msg = msg

    def __str__(self):

        return repr(self.msg)

if __name__ == '__main__':
    main()
