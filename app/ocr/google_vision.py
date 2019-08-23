import logging
import string
from xml.sax.saxutils import escape
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image
import requests
import os
from jinja2 import Environment, FileSystemLoader
import math

NEW_LINE_HYSTERESIS = 4
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
    trim_blocks=False)
VISION_CLIENT = vision.ImageAnnotatorClient()


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def ocr_image(image_uri, ocr_hints, max_pixels=36000000):
    """
    
    :param image_uri: The base IIIF Image API uri for the image 
    :param ocr_hints: 
    :param max_pixels: maximum number of pixels in the image (e.g. 36000000 for 6000 x 6000)
    :return: 
    """

    logging.debug("OCRing %s via google vision", image_uri)

    # New feature: requests the info.json before constructing the full image URI for fetching.
    with requests.Session() as s:
        info_response = s.get(image_uri, verify=False)
        if info_response.status_code == requests.codes.ok:
            info_json = info_response.json()
        else:
            info_json = None
        if info_json:
            height = info_json.get("height")
            width = info_json.get("width")
            if height and width:
                if int(height) * int(width) > max_pixels:
                    dimension = int(math.sqrt(max_pixels))
                    size_parameter = "!" + str(dimension) + "," + str(dimension)
                    logging.debug("%s is above max pixels and being constrained", image_uri)
                else:
                    logging.debug("%s is below the max pixels size.", image_uri)
                    size_parameter = "full"
            else:
                logging.error("Info.json did not contain a width and height for %s", image_uri)
                return None, None
        else:
            logging.error("Could not get an info.json response for %s", image_uri)
            return None, None

    full_image = ''.join([image_uri, '/full/', size_parameter, '/0/default.jpg'])

    with requests.Session() as s:
        image_response = s.get(full_image, verify=False)
        if not str(image_response.status_code).startswith("2"):
            logging.debug("Could not get source image")
            return None, None
        local_image = Image.open(io.BytesIO(image_response.content))
        image = types.Image(content=image_response.content)
        response = VISION_CLIENT.document_text_detection(image=image)
        texts = response.full_text_annotation

    if len(texts.pages) == 0:
        logging.info("No pages returned from Vision API")
        return None, None
    # logging.debug(vars(texts))

    source_page = texts.pages[0]
    page = {
        'id': 'page_1',
        'languages': get_language_codes(source_page.property.detected_languages),
        # TODO : its unclear from the documentation how to interpret multiple language codes in vision api
        'main_language': source_page.property.detected_languages[0].language_code,
        'width': local_image.width,
        'height': local_image.height,
        'careas': []
    }
    carea_count = 1
    par_count = 1
    line_count = 1
    word_count = 1

    for source_block in source_page.blocks:

        # TODO : check if block is text or image etc.

        carea = {
            'id': 'carea_' + str(carea_count),
            'bbox': get_bbox(source_block.bounding_box.vertices),
            'paragraphs': []
        }

        page['careas'].append(carea)
        carea_count += 1
        for source_paragraph in source_block.paragraphs:
            paragraph = {
                'id': 'par_' + str(par_count),
                'bbox': get_bbox(source_paragraph.bounding_box.vertices),
                'lines': []
            }
            carea['paragraphs'].append(paragraph)
            par_count += 1

            current_line_words = []
            last_word = None
            last_y = 0

            for source_word in source_paragraph.words:
                current_y = min([v.y for v in source_word.bounding_box.vertices])
                if (current_y > last_y + NEW_LINE_HYSTERESIS) and last_y > 0:
                    add_line_to_paragraph(current_line_words, line_count, paragraph)
                    current_line_words = []
                    last_word = None

                word_text = get_word_text(source_word)
                # if word text only punctuation and last_word not None, merge this text into that word and extend bbox
                if all(c in string.punctuation for c in word_text) and last_word is not None:

                    last_word['text'] += escape(word_text)
                    last_word['vertices'].extend(source_word.bounding_box.vertices)
                    last_word['bbox'] = get_bbox(last_word['vertices'])

                else:
                    word = {
                    'id': 'word_' + str(word_count),
                    'bbox': get_bbox(source_word.bounding_box.vertices),
                    'text': escape(word_text),
                    'vertices': source_word.bounding_box.vertices  # to generate line bbox
                    }
                    word_count += 1
                    current_line_words.append(word)
                    last_word = word
                last_y = current_y

            add_line_to_paragraph(current_line_words, line_count, paragraph)  # add last line

    hocr = render_template('vision_template.html', {"page": page })
    return hocr, 'hocr'


def add_line_to_paragraph(current_line_words, line_count, paragraph):
    line = {
        'id': 'line_' + str(line_count),
        'bbox': get_bbox([vertex for w in current_line_words for vertex in w['vertices']]),
        'words': current_line_words
    }
    line_count += 1
    paragraph['lines'].append(line)


def get_bbox(vertices):

    # # if it turns out these aren't always rectangles then obtain max and min xy across all vertices
    # return str(vertices._values[0].x) + ' ' + str(vertices._values[0].y) + ' ' \
    #        + str(vertices._values[1].x) + ' ' + str(vertices._values[1].y)

    return str(min([v.x for v in vertices])) + ' ' + \
           str(min([v.y for v in vertices])) + ' ' + \
           str(max([v.x for v in vertices])) + ' ' + \
           str(max([v.y for v in vertices]))


def get_word_text(word):

    word_text = ''
    for s, symbol in enumerate(word.symbols):
        word_text = word_text + symbol.text
    return word_text


def get_language_codes(detected_languages):

    return detected_languages[0].language_code if detected_languages else ""


def main():

    logging.basicConfig(filename="vision-test.log",
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', )

    res = ocr_image("https://dlc.services/iiif-img/6/1/473cc91e-689a-43e9-a52d-8a12f100bee2", {})
    print(res)


if __name__ == "__main__":
    main()
