import lxml.html
import requests

class LeoParser():
    def __init__(self):
        self._content = ''

    def load_from_file(self, path: str):
        with open(path, 'r') as f_dsc:
            self._content = f_dsc.read()
            f_dsc.close()

    def __str__(self):
        return '<LeoParser ({})>'.format(hex(id(self)))
