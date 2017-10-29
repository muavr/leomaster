# -*- coding: utf-8 -*-

import unittest
from leoparser.leoparser import LeoParser


class LeoParserTest(unittest.TestCase):
    TEST_DATA_PATH = './data/leo_page_content.html'

    def get_parser(self):
        return LeoParser()

    def get_content(self):
        with open(self.TEST_DATA_PATH, 'r', encoding='utf-8') as f_dsc:
            content = f_dsc.read()
            f_dsc.close()
        return content

    def test_to_str(self):
        lp = self.get_parser()
        object_id_in_hex = hex(id(lp))
        expected_value = '<LeoParser ({})>'.format(object_id_in_hex)
        self.assertEqual(lp.__str__(), expected_value)

    def test_loading_from_file(self):
        lp = self.get_parser()
        lp.load_from_file(self.TEST_DATA_PATH)
        expected_value = self.get_content()

        self.assertEqual(lp._content, expected_value)

if __name__ == '__main__':
    unittest.main()
