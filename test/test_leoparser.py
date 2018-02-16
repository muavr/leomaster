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

    def test_parsing_currency(self):
        lp = self.get_parser()
        self.assertEqual((100, 0), lp.parse_currency('100 рублей'))
        self.assertEqual((100, 0), lp.parse_currency('100 руб'))
        self.assertEqual((90, 0), lp.parse_currency('90 р'))
        self.assertEqual((100, 0), lp.parse_currency('100рублей'))
        self.assertEqual((100, 0), lp.parse_currency('100руб'))
        self.assertEqual((90, 0), lp.parse_currency('90р'))

    def test_parsing_duration(self):
        lp = self.get_parser()
        self.assertEqual(0, lp.parse_duration('1'))
        self.assertEqual(0, lp.parse_duration('0 ч'))
        self.assertEqual(3600, lp.parse_duration('1 ч'))
        self.assertEqual(3600, lp.parse_duration('1 час'))
        self.assertEqual(10800, lp.parse_duration('3 часа'))
        self.assertEqual(18000, lp.parse_duration('5 часов'))

    def test_parsing_date(self):
        pass




if __name__ == '__main__':
    unittest.main()
