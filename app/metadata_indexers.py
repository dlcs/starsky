import ftfy
from bs4 import BeautifulSoup


def get_words(text, text_format):

    if text_format == "hocr" or text_format == 'alto':
        return get_rich_words(text, text_format)
    else:
        # plaintext
        return get_plaintext_words(text)


def get_rich_words(text, text_format):

    soup = BeautifulSoup(text, "html.parser")

    word_index = []
    start_index = {}
    count = 0  # keep a running number of the words
    # iterate through lines in the hOCR
    char_count = 0  # keep a running count of character offset
    line_count = 0  # start at 1 below, do we care?
    confidence_total = 0

    lines = get_lines_from_soup(soup, text_format)
    for line in lines:

        line_count += 1
        # line bounds = get_line_bounds(line, format)
        line_bounds = None
        words = get_words_from_line(line, text_format)
        for word in words:

            count += 1
            word_dict = get_word_dict(word, text_format, line_bounds, line_count, count, char_count)
            char_count = char_count + len(word_dict['text']) + 1
            start_index[int(word_dict['start_idx'])] = len(word_index)
            if 'confidence' in word_dict:
                confidence_total += word_dict['confidence']
            word_index.append(word_dict)

    if confidence_total > 0 and count > 0:
        confidence = (confidence_total / count)
    else:
        confidence = 0

    return word_index, start_index, confidence


def get_line_bounds(line):

    return [0,0,0,0]


def get_lines_from_soup(soup, text_format):

    if text_format == "hocr":
        return soup.find_all("span", class_="ocr_line")

    else:  # alto
        return soup.find_all("textline")


def get_words_from_line(line, text_format):

    if text_format == "hocr":
        words = line.find_all("span", class_="ocrx_word")
        if words is None:
            words = line.split()

    else:  # alto
        words = line.find_all("string")

    return words


def get_word_dict(word, text_format, line_bounds, line_count, count, char_count):

    # build a dictionary of word properties
    word_dict = {}

    if text_format == "hocr":

        # <span class='ocrx_word' id='word_1_35' title='bbox 138 880 250 908; x_wconf 67' lang='eng'
        #  dir='ltr'>courtesy</span>
        #
        # or - just a string!

        word_dict['id'] = str(count)
        word_dict['line_number'] = line_count
        word_dict['start_idx'] = char_count

        if isinstance(word, basestring):

            word_dict['end_idx'] = (char_count + len(word))
            word_dict['text'] = ftfy.fix_text(word)

        else:

            bbox = word['title'].split(';')[0].split()[1:]

            word_dict['start_x'] = int(bbox[0])
            word_dict['start_y'] = int(bbox[1])
            word_dict['end_x'] = int(bbox[2])
            word_dict['end_y'] = int(bbox[3])

            word_dict['text'] = ftfy.fix_text(word.text)
            word_dict['end_idx'] = (char_count + len(word_dict['text']))

            word_dict['width'] = word_dict['end_x'] - word_dict['start_x']
            word_dict['height'] = word_dict['end_y'] - word_dict['start_y']

            parts = word['title'].split(';')
            if len(parts) > 1 and parts[1].split()[0] == "x_wconf":
                word_dict['confidence'] = int(word['title'].split(';')[1].split()[-1])

    else:  # alto

        #  <String ID="Word_208" HPOS="756" VPOS="798" WIDTH="67" HEIGHT="37" CONTENT="the" />

        word_dict['text'] = word['content']
        word_dict['id'] = str(count)  # running ID
        word_dict['line_number'] = line_count
        word_dict['start_idx'] = char_count
        word_dict['end_idx'] = char_count + len(word_dict['text'])

        word_dict['start_x'] = int(word['hpos'])
        word_dict['start_y'] = int(word['vpos'])
        word_dict['width'] = int(word['width'])
        word_dict['end_x'] = word_dict['start_x'] + word_dict['width']
        word_dict['height'] = int(word['height'])
        word_dict['end_y'] = word_dict['start_y'] + word_dict['height']

    return word_dict


def get_plaintext_words(plaintext):

    word_index = []
    start_index = {}

    count = 0
    char_count = 0

    for word in plaintext.split():
        word_dict = {
            "text": word,
            "id": count,
            "start_idx": char_count,
            "end_idx": char_count + len(word)
        }
        word_index.append(word_dict)
        start_index[char_count] = count

        count += 1
        char_count += len(word) + 1

    return word_index, start_index, 0


