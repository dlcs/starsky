import unittest
import starsky_ingest


class TextOCRFormat(unittest.TestCase):

    def test_alto(self):

        alto = open('fixtures/b20402533_0010.xml').read()
        starsky = starsky_ingest.Starsky()
        format = starsky.identify_format(alto)
        self.assertEqual(format, 'alto')

    def test_hocr(self):

        hocr = open('fixtures/vet1.html').read()
        starsky = starsky_ingest.Starsky()
        format = starsky.identify_format(hocr)
        self.assertEqual(format, 'hocr')

    def test_text(self):

        neither = "This is just a string"
        starsky = starsky_ingest.Starsky()
        format = starsky.identify_format(neither)
        self.assertEqual(format, "text")
