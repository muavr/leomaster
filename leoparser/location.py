# -*- coding: utf-8 -*-


class Location(object):
    def __init__(self, title: str='', lat: float=0.0, lng: float=0.0):
        self._title = title
        self._lat = lat
        self._lng = lng

    def get_title(self):
        return self._title

    def get_coordinates(self):
        return self._lat, self._lng

    def get_latitude(self):
        return self._lat

    def get_longitude(self):
        return self._lng
