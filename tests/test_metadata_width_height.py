import unittest
import starsky_ingest


class TextMetadataWidthHeight(unittest.TestCase):

    def test_hocr(self):

        hocr = open('fixtures/vet1.html').read()
        width, height = starsky_ingest.Starsky.get_width_height(hocr, 'hocr')
        self.assertEqual(1205, width)
        self.assertEqual(2000, height)

    def test_alto(self):

        alto = open('fixtures/b20402533_0010.xml').read()
        width, height = starsky_ingest.Starsky.get_width_height(alto, 'alto')
        self.assertEqual(2319, width)
        self.assertEqual(3243, height)
