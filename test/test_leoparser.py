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

    def test_to_str(self):
        lp = self.get_parser()
        object_id_in_hex = hex(id(lp))
        expected_value = '<LeoParser ({})>'.format(object_id_in_hex)
        self.assertEqual(lp.__str__(), expected_value)

if __name__ == '__main__':
    unittest.main()
