import logging
from urllib import quote_plus
import concurrent.futures
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify, send_file
import json
import StringIO
import aws
import settings
import requests
from PIL import Image, ImageDraw


app = Flask(__name__)


def main():

    app.run(threaded=True, debug=True, port=5000, host='0.0.0.0')


@app.route('/coords/', methods=['POST'])
def coords_service():

    """
    example request:

    {
       'images': [
         {
           'imageURI' : <uri>,
           'positions' : [ [25, 31], 100,110], // list of integers or integer arrays * representing ordinal character posisitions within text for image
           'width' : 1024, // height and width of image to be presented
           'height' : 768 // text server scales from stored boxes
        }
      ]
    }

    """

    request_data = request.get_json()
    images = request_data.get("images")

    results = get_concurrent_coords(images)

    response_data = {
        "images": results
    }

    return jsonify(response_data)


def get_concurrent_coords(images):
    results = []
    # TODO pass in text index to reduce loading
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_coords, image): image for image in images}
        for future in concurrent.futures.as_completed(futures):
            image = futures[future]
            try:
                image_result = future.result()
            except:
                logging.exception("Error in future")
            else:
                results.append(image_result)
    return results


@app.route('/coordsimage/<image_index>/', methods=['POST'])
def coords_image_service(image_index):

    # this obtains the same data as get_concurrent_coords but draws boxes over the source image

    request_data = request.get_json()
    images = request_data.get("images")

    results = get_concurrent_coords(images)

    width = request_data['images'][int(image_index)]['width']
    height = request_data['images'][int(image_index)]['height']

    base_uri = request_data['images'][int(image_index)]['imageURI']
    image_uri = base_uri + "/full/%s,%s/0/default.jpg" % (width, height)

    r = requests.get(image_uri)
    image = Image.open(StringIO.StringIO(r.content))

    for output_image in results:
        if output_image.get('image_uri') == base_uri:
            boxes = output_image.get('xywh')
            draw = ImageDraw.Draw(image)
            for box in boxes:
                x, y, w, h = box.split(',')
                draw.rectangle(((int(x), int(y)),  (int(x) + int(w), int(y) + int(h))), outline="green")
                draw.rectangle(((int(x) - 1, int(y) -1), (int(x) + int(w) + 1, int(y) + int(h) + 1)), outline="green")

    return serve_pil_image(image)


def serve_pil_image(pil_img):

    img_io = StringIO.StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/plaintext/', methods=['GET'])
def plaintext_service():

    image_uri = request.args.get('imageURI')

    s3 = aws.get_s3_resource()
    text_data = get_text_index(s3, image_uri)
    if text_data is None:
        return jsonify({image_uri: ""})
    word_index = text_data.get("word_index")

    text = " ".join(map(lambda w: w['text'], word_index))
    return jsonify({image_uri: text})


@app.route('/plaintextlines/', methods=['GET'])
def plaintextlines_service():

    image_uri = request.args.get('imageURI')
    width = request.args.get('width')
    height = request.args.get('height')

    s3 = aws.get_s3_resource()
    text_data = get_text_index(s3, image_uri)
    if text_data is None:
        return jsonify({image_uri: []})
    word_index = text_data.get("word_index")

    o_width = text_data.get("width")
    o_height = text_data.get("height")

    scale_w = float(width) / float(o_width)
    scale_h = float(height) / float(o_height)

    if 'line_number' not in word_index[0]:
        return jsonify({"error": "plaintext lines not available"}), 415

    lines = []
    line = ""
    line_boxes = []
    current_line = -1
    for word in word_index:
        if word['line_number'] != current_line:
            if current_line != -1:
                lines.append({"text": line, "xywh": box_join(line_boxes)})
                line = ""
                line_boxes = []
            current_line = word['line_number']
        line += word['text'] + " "
        line_boxes.append(get_box(word, scale_w, scale_h))
    return jsonify({"lines": lines})


@app.route('/confidence/', methods=['POST'])
def confidence_service():

    results = []
    request_data = request.get_json()
    images = request_data.get("images")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_confidence, image): image for image in images}
        for future in concurrent.futures.as_completed(futures):
            image = futures[future]
            try:
                word_result = future.result()
            except:
                logging.exception("Error in future")
            else:
                results.append(word_result)

    response_data = {
        "images": results
    }
    return jsonify(response_data)


def get_confidence(image):

    s3 = aws.get_s3_resource()
    result = {"imageURI": image}
    text_data = get_text_index(s3, image)
    if text_data is not None:
        confidence = text_data.get('confidence')
        if confidence is not None:
            result['confidence'] = confidence
    return result


def get_coords(image):

    """

    {"positions": [[25, 31], 100, 110], "height": 768, "width": 1024, "imageURI": "http://aplaceforstuff.co.uk/x/"}

    """

    boxes = []
    s3 = aws.get_s3_resource()
    image_uri = image.get("imageURI")
    output = {
        "image_uri": image_uri
    }
    positions = image.get("positions")
    text_data = get_text_index(s3, image_uri)
    if text_data is None:
        return output

    o_width = text_data.get("width")
    o_height = text_data.get("height")
    if o_width is None or o_height is None:
        output = {
            "imageURI": image_uri,
            "message": "no coordinates available"
        }
        return output

    word_index = text_data.get("word_index")
    start_index = text_data.get("start_index")

    width = image.get("width")
    height = image.get("height")

    scale_w = float(width) / float(o_width)
    scale_h = float(height) / float(o_height)

    if word_index is None:
        raise Exception
        # TODO : handle better!
    for phrase_or_position in positions:
        if isinstance(phrase_or_position, int):
            # single word
            idx = start_index.get(str(phrase_or_position))
            if idx is None:
                # todo handle
                pass
            word_data = word_index[idx]
            p_boxes = box_join(get_box(word_data, scale_w, scale_h))
        else:
            # phrase
            phrase_boxes = []
            for position in phrase_or_position:
                idx = start_index.get(str(position))
                if idx is None:
                    # todo handle
                    pass
                word_data = word_index[idx]
                position_box = get_box(word_data, scale_w, scale_h)
                phrase_boxes.append(position_box)
            p_boxes = box_join(phrase_boxes)
        boxes.append(p_boxes)

    output['phrases'] = boxes
    return output


def get_box(box_data, scale_w, scale_h):

    return [box_data.get("line_number"), 1,  int(box_data.get("start_x") * scale_w), int(box_data.get("start_y") * scale_h),
            int(box_data.get("width") * scale_w), int(box_data.get("height") * scale_h)]


def box_join(boxes):

    # check for list of boxes
    if any(isinstance(i, list) or isinstance(i, tuple) for i in boxes):

        super_boxes = []
        current_line = -1
        min_x, max_x, min_y, max_y = None, None, None, None

        # join (sort by line, while same line, join, start again on new line
        boxes.sort(key=lambda x: x[0])

        box_count = 0
        for box in boxes:
            if box[0] != current_line:
                if current_line != -1:
                    super_boxes.append([current_line, box_count, min_x, min_y, (max_x - min_x), (max_y - min_y)])
                    min_x, max_x, min_y, max_y = None, None, None, None
                    box_count = 0
            current_line = box[0]
            box_count += 1
            if min_x is None or box[2] < min_x:
                min_x = box[2]
            if min_y is None or box[3] < min_y:
                min_y = box[3]
            if max_x is None or box[2] + box[4] > max_x:
                max_x = box[2] + box[4]
            if max_y is None or box[2] + box[4] > max_y:
                max_y = box[3] + box[5]
        super_boxes.append([current_line, box_count, min_x, min_y, (max_x - min_x), (max_y - min_y)])

        box_objects = map(box_to_object, super_boxes)
        return box_objects

    else:
        # single box
        return [box_to_object(boxes)]


def box_to_object(box):

    return {
        "count": box[1],
        "xywh": ",".join(map(str, box[2:]))
    }


def get_text_index(s3, image_uri):

    encoded_uri = quote_plus(image_uri)
    try:
        obj = aws.get_s3_object(s3, settings.INDEX_BUCKET, encoded_uri)
    except ClientError:
        logging.debug("Metadata not found in S3 for %", image_uri)
        return None
    if obj.status != 200:
        logging.error("Could not get metadata from S3 for %s", image_uri)
        return None
    body = obj.get("Body").read()
    return json.loads(body)


def set_logging():
    logging.basicConfig(filename="starsky_service.log",
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', )
    logging.getLogger('boto').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

if __name__ == "__main__":
    set_logging()
    main()
