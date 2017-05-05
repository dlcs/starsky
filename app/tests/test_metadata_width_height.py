import unittest
import starsky_ingest


class TextMetadataWidthHeight(unittest.TestCase):

    def test_hocr(self):

        hocr = open('app/tests/fixtures/vet1.html').read()
        width, height, canvas_width, canvas_height = starsky_ingest.Starsky.get_width_height(hocr, 'hocr', "https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500")
        self.assertEqual(1205, width)
        self.assertEqual(2000, height)
        self.assertEqual(1929, canvas_width)
        self.assertEqual(2849, canvas_height)

    def test_hocr_nosize(self):

        hocr = open('app/tests/fixtures/ocropus_trained.html').read()
        width, height, canvas_width, canvas_height = starsky_ingest.Starsky.get_width_height(hocr, 'hocr', "https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500")
        self.assertEqual(1929, width)
        self.assertEqual(2849, height)
        self.assertEqual(1929, canvas_width)
        self.assertEqual(2849, canvas_height)

    def test_alto(self):

        alto = open('app/tests/fixtures/b20402533_0010.xml').read()
        width, height, canvas_width, canvas_height = starsky_ingest.Starsky.get_width_height(alto, 'alto', "https://dlcs.io/iiif-img/50/1/000214ef-74f3-4ec2-9a5f-3b79f50fc500")
        self.assertEqual(2319, width)
        self.assertEqual(3243, height)
        self.assertEqual(1929, canvas_width)
        self.assertEqual(2849, canvas_height)
