# -*- coding: utf-8 -*-

import re
import sys
import pytz
import json
import lxml
import lxml.html
import datetime
from decimal import *


class ExtractionError(Exception):
    def __init__(self, xpath, extracted, message='', *args, **kwargs):
        self.message = message
        self._extracted = extracted
        self.xpath = xpath

    @property
    def extracted(self):
        if isinstance(self._extracted, lxml.html.HtmlElement):
            return self._extracted.xpath('string(.//text())')
        return str(self._extracted)

    def __str__(self):
        return '<ExtractionError>(xpath= "{0}", extracted= "{1}")'.format(self.xpath, self.extracted)


class EmptyExtractionError(ExtractionError):
    def __init__(self, xpath, message='', *args, **kwargs):
        super(EmptyExtractionError, self).__init__(xpath, '', message, *args, **kwargs)

    def __str__(self):
        return '<EmptyExtractionError>(xpath= "{0}")'.format(self.xpath)


class ParsingExtractionError(ExtractionError):
    def __init__(self, xpath, extracted, patterns, message='', *args, **kwargs):
        self._patterns = patterns
        super(ParsingExtractionError, self).__init__(xpath, extracted, message, *args, **kwargs)

    def __str__(self):
        return '<ParsingExtractionError>(xpath= "{0}", extracted= "{1}"):\n{2}'.format(
            self.xpath, self.extracted, '\t\n'.join(self.patterns))

    @property
    def patterns(self):
        if self._patterns:
            if isinstance(self._patterns[0], type(re.compile(''))):
                return ('/' + str(p.pattern) + '/' for p in self._patterns)
            else:
                return ('"' + str(p) + '"' for p in self._patterns)
        return tuple()


def find_first_match(f):
    def wrapper(self, value: str):
        match = self._get_first_math(self.REGEX_PATTERNS, value)
        if match:
            return f(self, match.group(1))
        raise ParsingExtractionError(self._xpath, value, self.REGEX_PATTERNS)

    return wrapper


class FieldExtractor(object):
    REGEX_PATTERNS = tuple()

    def __init__(self, xpath: str):
        self._xpath = xpath

    def extract_from(self, section):
        try:
            value = section.xpath(self._xpath)
            if value:
                return self._post_process(value)
            raise EmptyExtractionError(self._xpath, '')
        except lxml.etree.XPathEvalError as err:
            raise ExtractionError(self._xpath, '') from err

    def _post_process(self, value: str):
        return value

    @staticmethod
    def _get_first_math(patterns, value):
        for regex in patterns:
            match = regex.search(value)
            if match:
                return match


class StringFieldExtractor(FieldExtractor):
    pass


class IntFieldExtractor(FieldExtractor):
    REGEX_PATTERNS = (
        re.compile('(\d+)', re.UNICODE),
    )

    @find_first_match
    def _post_process(self, value):
        return int(value)


class DateTimeFieldExtractor(FieldExtractor):

    def __init__(self, xpath: str, date_format: str = '%d.%m.%Y %H:%M', tz: str = 'Europe/Moscow'):
        self._format = date_format
        self._tz = tz
        super(DateTimeFieldExtractor, self).__init__(xpath)

    def _post_process(self, value: str):
        """
        Splits passed string and expect 3 parts.
        Omits the {1} element it is a full day name
        :param value:
        :return:
        """
        try:
            string_date = '{0} {2}'.format(*value.split())
            date = datetime.datetime.strptime(string_date, self._format)
            tz = pytz.timezone(self._tz)
            return tz.localize(date, is_dst=False)
        except ValueError:
            raise ParsingExtractionError(self._xpath, value, [self._format])


class CurrencyFieldExtractor(FieldExtractor):
    REGEX_PATTERNS = (
        re.compile('^(\d+)\s*р', re.UNICODE),
    )

    @find_first_match
    def _post_process(self, value):
        return Decimal(value)


class DurationFieldExtractor(FieldExtractor):
    """
    Returns time in seconds.
    :param field:
    :return:
    """
    REGEX_PATTERNS = (
        re.compile('(\d+(?:[\.,]\d+)?)\s*ч', re.UNICODE),
    )

    @find_first_match
    def _post_process(self, value):
        value = str(value).replace(',', '.')
        return int(Decimal(value) * 60 * 60)


class LeoParser(object):
    def __init__(self, xpath, key_field):
        self._key_field = key_field
        self._xpath = xpath
        self._extractors = dict()

    def parse_to_dict(self, content):
        html = lxml.html.document_fromstring(content)
        sections = html.xpath(self._xpath)
        returning_dict = dict()

        for section in sections:
            master_class = dict()
            for field, extractor in self._extractors.items():
                try:
                    master_class[field] = extractor.extract_from(section)
                except ExtractionError as err:
                    print(err, sys.stderr)
                    raise err
            returning_dict[master_class.get(self._key_field)] = master_class

        return returning_dict

    def parse_to_json(self, content, prettify=False):
        parsed_dict = self.parse_to_dict(content)
        if prettify:
            return json.dumps(parsed_dict, default=str, indent=4)
        else:
            return json.dumps(parsed_dict, default=str)

    def parse_to_text(self, content):
        parsed_dict = self.parse_to_dict(content)
        returning_string = ''

        for mc_id in parsed_dict:
            mc_dict = parsed_dict[mc_id]
            for field, value in mc_dict.items():
                returning_string += '{0}= {1}\n'.format(field, value)
            returning_string += '=' * 20 + '\n'
        return returning_string

    def register_extractor(self, field_name, extractor):
        self._extractors[field_name] = extractor


class LeoParserFabric:
    def __init__(self, config: dict):
        self._config = config
        self._extractors = {
            'string': StringFieldExtractor,
            'integer': IntFieldExtractor,
            'dateTime': DateTimeFieldExtractor,
            'currency': CurrencyFieldExtractor,
            'duration': DurationFieldExtractor
        }

    def create_parser(self):
        sections_dsc = self._config.get('xpaths').pop('sections')
        xpath_sections = sections_dsc.get('xpath')
        key_field = sections_dsc.get('key_field')

        parser = LeoParser(xpath_sections, key_field)
        for name, extractor in self._config.get('xpaths').items():
            extractor_class = self._extractors.get(extractor.get('type'))
            args = extractor.get('args')
            kwargs = extractor.get('kwargs')
            extractor_xpath = extractor.get('xpath')
            parser.register_extractor(name, extractor_class(extractor_xpath, *args, **kwargs))
        return parser


if __name__ == '__main__':
    content_path = '../test/data/leo_page_content_201805.html'
    config_path = './parser_config.json'

    with open(content_path, 'r', encoding='utf8') as f_dsc:
        content = f_dsc.read()
        f_dsc.close()

    with open(config_path, 'r', encoding='utf8') as f_dsc:
        config = f_dsc.read()
        f_dsc.close()

    config_dict = json.loads(config)

    lp_fabric = LeoParserFabric(config_dict)

    lp = lp_fabric.create_parser()

    print(lp.parse_to_json(content, prettify=True))
