# -*- coding: utf-8 -*-

import lxml.html
import requests


class LeoParser(object):
    def __init__(self):
        self._content = ''

    def load_from_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f_dsc:
            self._content = f_dsc.read()
            f_dsc.close()

    def __str__(self):
        return '<LeoParser ({})>'.format(hex(id(self)))
