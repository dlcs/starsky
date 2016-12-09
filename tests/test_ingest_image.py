import unittest

import starsky_ingest

import json


class TestIngest(unittest.TestCase):

    def test_process_message(self):

        message = Message()
        message.body = json.dumps(
            {
                "images":
                [
                    {"imageURI": "https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500"}
                ]
            })
        s = starsky_ingest.Starsky()
        s.init()
        s.process_message(message)


class Message:

    def __init__(self):
        self.message = ""
