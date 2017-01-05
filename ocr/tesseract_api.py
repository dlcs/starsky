import logging
from tesserocr import PyTessBaseAPI
import requests
from PIL import Image, ImageFile
from StringIO import StringIO
ImageFile.LOAD_TRUNCATED_IMAGES = True


def ocr_image(image_uri, ocr_hints):

    # OCR image to hocr, uses API call to avoid temporary file
    # TODO : support hints - e.g. DPI via 'well known' key names, trained language, etc.
    logging.debug("OCRing %s", image_uri)

    # image uri is IIIF endpoint
    # TODO : revisit - update for max vs full?
    full_image = ''.join([image_uri, '/full/full/0/default.jpg'])
    r = requests.get(full_image)

    if r.status_code == 200:

        with PyTessBaseAPI() as api:
            image = Image.open(StringIO(r.content))
            api.SetImage(image)
            hocr = api.GetHOCRText(0)
    else:
        raise IOError("Could not obtain %s", image_uri)

    return hocr, 'hocr'
