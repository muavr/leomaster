import unittest
from leoparser.leoparser import LeoParser


class LeoparserTest(unittest.TestCase):
    TEST_DATA_PATH = './data/leo_page_content.html'

    def  get_parser(self):
        return LeoParser()

    def  get_content(self):
        content = ''
        with open(TEST_DATA_PATH, 'r') as f_dsc:
            content = f_dsc.read()
            f_dsc.close()
        return content

if __name__ == '__main__':
    unittest.main()
