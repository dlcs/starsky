import unittest
import starsky_service


class TextBoxJoinSingleLine(unittest.TestCase):

    def test_single_box(self):

        boxes = [3, 1, 887, 351, 122, 34]
        expected_result = [{"count": 1, "xywh": "887,351,122,34"}]
        result = starsky_service.box_join(boxes)
        self.assertEqual(expected_result, result)

    def test_two_boxes(self):

        boxes = [[3, 1, 887, 351, 122, 34], [3, 1, 1100, 351, 122, 34]]
        expected_result = [{"count": 2, "xywh": "887,351,335,34"}]
        result = starsky_service.box_join(boxes)
        self.assertEqual(expected_result, result)


class TestBoxJoinMultiLine(unittest.TestCase):

    def test_multiline(self):

        boxes = [[2, 1, 1155, 276, 149, 37],[2, 1, 1332, 290, 191, 26], [3, 1, 582, 348, 91, 34]]
        expected_result = [{"count": 2, "xywh": "1155,276,368,40"}, {"count": 1, "xywh": "582,348,91,34"}]
        result = starsky_service.box_join(boxes)
        self.assertEqual(expected_result, result)



