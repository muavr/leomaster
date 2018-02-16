# -*- coding: utf-8 -*-

import re
import pytz
import lxml.html
import datetime


class LeoParser(object):
    CURRENCY_PATTERNS = [
            re.compile('^(\d+)\s*р', re.UNICODE),
        ]

    DURATION_PATTERNS = [
            re.compile('(\d+)\s*ч', re.UNICODE),
        ]

    def __init__(self):
        self._content = ''

    def load_from_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f_dsc:
            self._content = f_dsc.read()
            f_dsc.close()

    def parse(self):
        masterclasses = list()
        sections = self.extract_sections()

        for section in sections:
            section_id = self.extract_id(section)
            if section_id:
                print('id = %s' % section_id)
                title = self.extract_title(section)
                print('title = %s' % title)
                location = self.extract_location(section)
                print('location = %s' % location)
                date = self.extract_date(section)
                print('date = %s' % date)
                description = self.extract_description(section)
                print('description = %s' % description)
                total_seats = self.extract_total_seats(section)
                print('total_seats = %s' % total_seats)
                available_seats = self.extract_available_seats(section)
                print('available_seats = %s' % available_seats)
                on_spot_price = self.extract_on_spot_price(section)
                print('on_spot_price = %d, %d' % on_spot_price)
                online_price = self.extract_online_price(section)
                print('online_price = %d, %d' % online_price)
                duration = self.extract_duration(section)
                print('duration = %s' % duration)
                age_limit = self.extract_age_limit(section)
                print('age_limit = %d' % age_limit)
                owner_name = self.extract_owner_name(section)
                print('owner_name = %s' % owner_name)

    @staticmethod
    def extract_int(section, xpath):
        value = 0
        parse_result = section.xpath(xpath)
        if parse_result:
            string_value = parse_result[0]
            value = int(string_value)
        return value

    @staticmethod
    def convert_string_to_int_or_return_zero(value):
        try:
            match = re.search('\d+', value)
            if match:
                value = match.group(0)
            value = int(value)
        except Exception:
            return 0
        return value

    @staticmethod
    def extract_string(section, xpath):
        value = ''
        parse_result = section.xpath(xpath)
        if parse_result:
            value = str(parse_result[0]).strip()
        return value

    @staticmethod
    def get_first_math(patterns, value):
        for regex in patterns:
            match = regex.search(value)
            if match:
                return match

    def extract_sections(self):
        html = lxml.html.document_fromstring(self._content)
        sections = html.xpath('//div[contains(@class, "masterclass clearfix")]')
        return sections

    def extract_currency(self, section, xpath):
        parse_result = self.extract_string(section, xpath)
        integer, fraction = self.parse_currency(parse_result)
        return integer, fraction

    def parse_currency(self, value):
        integer = 0
        fraction = 0
        match = self.get_first_math(self.CURRENCY_PATTERNS, value)
        if match:
            integer = self.convert_string_to_int_or_return_zero(match.group(1))
        return integer, fraction

    def parse_duration(self, value):
        seconds_in_minute = 60
        minutes_in_hours = 60
        seconds = 0
        match = self.get_first_math(self.DURATION_PATTERNS, value)
        if match:
            hours = self.convert_string_to_int_or_return_zero(match.group(1))
            seconds = (hours * minutes_in_hours * seconds_in_minute)
        return seconds

    def extract_id(self, section):
        section_id = self.extract_int(section, '(.//@id)[2]')
        return section_id

    def extract_title(self, section):
        title = self.extract_string(section, './/div[@class="mk_fulltitle"]//text()')
        return title

    def extract_location(self, section):
        return self.extract_string(section, './/div[@class="mk_place"]/a//text()')

    def extract_date(self, section):
        string_date = self.extract_string(section, './/div[@class="mk_time"]//text()')
        string_date = '{0} {2}'.format(*string_date.split())
        date = datetime.datetime.strptime(string_date, '%d.%m.%Y %H:%M')
        tz = pytz.timezone('Europe/Moscow')
        local_date = tz.localize(date, is_dst=False)
        return local_date

    def extract_description(self, section):
        description = self.extract_string(section, './/div[@class="col-xs-12 col-sm-8 mk-leftcol"][2]/p//text()[1]')
        return description

    def extract_age_limit(self, section):
        age_limit = self.extract_string(section, './/table[@class="mk_description"]/tbody/tr[1]/td[2]//text()')
        age_limit = self.convert_string_to_int_or_return_zero(age_limit)
        return age_limit

    def extract_owner_name(self, section):
        name = self.extract_string(section, './/table[@class="mk_description"]/tbody/tr[2]/td[2]//text()')
        return name

    def extract_duration(self, section):
        duration = self.extract_string(section, './/div[@class="col-xs-12 col-sm-8 mk-leftcol"][2]/p//text()[3]')
        duration = self.parse_duration(duration)
        return duration

    def extract_total_seats(self, section):
        seats = self.extract_int(section, './/tbody/tr/td[@class="p-count__cell"]//text()')
        return seats

    def extract_available_seats(self, section):
        seats = self.extract_int(section, './/tbody/tr/td[@class="free-place_cell"]//text()')
        return seats

    def extract_online_price(self, section):
        price = self.extract_currency(section, './/tbody/tr[last()]/td[2]//text()')
        return price[0], price[1]

    def extract_on_spot_price(self, section):
        title = self.extract_string(section, './/tbody/tr[last()-1]/td[1]//text()')
        if 'в магазине' in title:
            price = self.extract_currency(section, './/tbody/tr[last()-1]/td[2]//text()')
            return price[0], price[1]
        else:
            return self.extract_online_price(section)

    def __str__(self):
        return '<LeoParser ({})>'.format(hex(id(self)))

if __name__ == '__main__':
        lp = LeoParser()
        lp.load_from_file('../test/data/leo_page_content.html')
        lp.parse()