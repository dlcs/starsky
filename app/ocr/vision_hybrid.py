import tesseract_api
import google_vision
import logging
from bs4 import BeautifulSoup


def ocr_image(image_uri, ocr_hints):

    hocr = tesseract_api.ocr_image(image_uri, ocr_hints)
    confidence, typewritten = ocr_xray(hocr[0])
    if typewritten:
        logging.debug("Image %s looks typewritten, using Google Vision", image_uri)
        return google_vision.ocr_image(image_uri, ocr_hints)
    else:
        logging.debug("Image %s does not look typewritten, won't OCR", image_uri)
        return None


def ocr_xray(hocr_data):

    soup = BeautifulSoup(hocr_data, "html.parser")
    lines = soup.find_all("span", class_="ocr_line")
    count = 0
    conf_total = 0

    for line in lines:
        words = line.find_all("span", class_="ocrx_word")
        for word in words:
            count += 1
            word_soup = BeautifulSoup(str(word), "html.parser")
            confidence = int(word_soup.span['title'].split(';')[1].split()[-1])
            conf_total = conf_total + confidence

    if conf_total > 0 and count > 0:
        average_confidence = (conf_total / count)
    else:
        average_confidence = 0
    if average_confidence < 60:
        typewritten = False
    elif average_confidence > 70 and count < 3:
        typewritten = False
    else:
        typewritten = True
    return average_confidence, typewritten


def main():

    logging.basicConfig(filename="vision-hybrid-test.log",
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', )

    #res = ocr_image("https://dlcs-ida.org/iiif-img/2/1/M-1304_R-13_0175", {})
    res = ocr_image("https://dlcs.io/iiif-img/50/1/440021cf-3326-4840-94fc-ee3f33f8aa4b", {})
    print(res)

if __name__ == "__main__":
    main()
