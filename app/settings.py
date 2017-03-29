import os

MESSAGES_PER_FETCH = 5
POLL_INTERVAL = 20
PUSH_PLAINTEXT = True
ocr = os.environ.get('STARSKY_OCR')
if ocr is not None:
    OCR_PLUGIN = ocr
else:
    OCR_PLUGIN = "ocr.tesseract_api"
REGION = os.environ.get('STARSKY_AWS_REGION')  # e.g. 'eu-west-1'
INGEST_QUEUE = os.environ.get('STARSKY_INGEST_QUEUE')  # e.g. 'starsky-ingest-queue'
ERROR_QUEUE = os.environ.get('STARSKY_ERROR_QUEUE')  # e.g. 'starsky-error-queue'
MANIFEST_QUEUE = os.environ.get('STARSKY_MANIFEST_QUEUE')  # e.g. 'starsky-error-queue'
TEXT_QUEUE = os.environ.get('STARSKY_TEXT_QUEUE')  # e.g. 'starsky-text-queue'
TEXT_METADATA_BUCKET = os.environ.get('STARSKY_TEXT_METADATA_BUCKET')  # e.g. 'starsky-text-meta'
INDEX_BUCKET = os.environ.get('STARSKY_INDEX_BUCKET')  # e.g. 'starsky-index'

