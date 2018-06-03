# -*- coding: utf-8 -*-

import unittest
from decimal import *
from datetime import datetime
from leoparser.leoparser import DurationFieldExtractor, CurrencyFieldExtractor, DateTimeFieldExtractor


class LeoParserTest(unittest.TestCase):
    TEST_DATA_PATH = './data/leo_page_content_201805.html'

    def test_parsing_currency(self):
        extractor = CurrencyFieldExtractor('')
        self.assertEqual(Decimal(100), extractor._post_process('100 рублей'))
        self.assertEqual(Decimal(100), extractor._post_process('100 руб'))
        self.assertEqual(Decimal(90), extractor._post_process('90 р'))
        self.assertEqual(Decimal(100), extractor._post_process('100рублей'))
        self.assertEqual(Decimal(100), extractor._post_process('100руб'))
        self.assertEqual(Decimal(90), extractor._post_process('90р'))

    def test_parsing_duration(self):
        extractor = DurationFieldExtractor('')
        self.assertEqual(0, extractor._post_process('0 ч'))
        self.assertEqual(3600, extractor._post_process('1 ч'))
        self.assertEqual(3600, extractor._post_process('1 час'))
        self.assertEqual(10800, extractor._post_process('3 часа'))
        self.assertEqual(18000, extractor._post_process('5 часов'))
        self.assertEqual(5400, extractor._post_process('1.5 ч'))
        self.assertEqual(5400, extractor._post_process('1,5 ч'))

    def test_parsing_date(self):
        time_format = '%Y-%m-%d %H:%M:%S%z'
        extractor = DateTimeFieldExtractor('', tz='Europe/Moscow')
        self.assertEqual(datetime.strptime('2018-07-19 18:00:00+0300', time_format),
                         extractor._post_process('19.07.2018 четверг 18:00'))

        extractor = DateTimeFieldExtractor('', tz='Europe/Ulyanovsk')
        self.assertEqual(datetime.strptime('2018-07-19 18:00:00+0400', time_format),
                         extractor._post_process('19.07.2018 четверг 18:00'))


if __name__ == '__main__':
    unittest.main()
