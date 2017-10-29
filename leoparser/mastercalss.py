# -*- coding: utf-8 -*-

import datetime
from leoparser.location import Location


class Masterclass(object):
    def __init__(self, title: str = '', date: datetime = datetime.datetime.now(tz=None)):
        self.date = date
        self.title = title
        self.location = Location()
        self.description = ''
        self.duration = 0
        self.age_limit = 0
        self.owner_name = ''
        self.total_seats = 0
        self.available_seats = 0
        self.online_price = 0, 0
        self.on_spot_price = 0, 0
        self.tags = set()

    def set_date(self, date: datetime):
        self.date = date

    def set_title(self, text: str):
        self.title = text

    def set_location(self, location: Location):
        self.location = location

    def set_description(self, text: str):
        self.description = text

    def set_duration(self, sec: int):
        self.duration = sec

    def set_age_limit(self, years: int):
        self.age_limit = years

    def set_owner_name(self, name: str):
        self.owner_name = name

    def set_total_seats(self, count: int):
        self.total_seats = count

    def set_available_seats(self, count: int):
        self.available_seats = count

    def set_online_price(self, integer_part: int, fractional_part: int):
        self.online_price = integer_part, fractional_part

    def set_on_spot_price(self, integer_part: int, fractional_part: int):
        self.on_spot_price = integer_part, fractional_part

    def add_tag(self, tag: str):
        self.tags.add(tag)
