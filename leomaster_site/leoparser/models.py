from django.db import models


class Rule(models.Model):
    name = models.TextField(verbose_name='name', unique=True, blank=False)
    xpath = models.TextField(verbose_name='xpath', blank=False)
    typeof = models.ForeignKey('TypeOf', on_delete=models.CASCADE)
    parent = models.ForeignKey('Rule', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('name', )

    def apply(self, element):
        res = element.xpath(self.xpath)
        return self.typeof.convert(res)

    def __str__(self):
        return '%s::%s::%s' % (self.name, self.xpath, self.typeof)

    def __repr__(self):
        return '<Rule>::%s' % (self.name,)

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'xpath': self.xpath,
                'type': self.typeof.name,
                'parent': self.parent.id if self.parent else None,
                'children': [c.id for c in self.children.all()]}


class TypeOf(models.Model):

    T_CONTAINER = 'container'
    T_CURRENCY = 'currency'
    T_DATE = 'date'
    T_DATETIME = 'datetime'
    T_FLOAT = 'float'
    T_INTEGER = 'integer'
    T_STRING = 'string'
    T_TIME = 'time'

    options = [
        (T_CONTAINER, T_CONTAINER),
        (T_CURRENCY, T_CURRENCY),
        (T_DATE, T_DATE),
        (T_DATETIME, T_DATETIME),
        (T_FLOAT, T_FLOAT),
        (T_INTEGER, T_INTEGER),
        (T_STRING, T_STRING),
        (T_TIME, T_TIME),
    ]

    name = models.TextField(verbose_name='name', choices=options, unique=True, blank=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.converters = {
            self.T_CONTAINER: self.to_container,
            self.T_CURRENCY: self.to_currency,
            self.T_DATE: self.to_date,
            self.T_DATETIME: self.to_datetime,
            self.T_FLOAT: self.to_float,
            self.T_INTEGER: self.to_integer,
            self.T_STRING: self.to_string,
            self.T_TIME: self.to_time,
        }

    class Meta:
        ordering = ('name', )

    def convert(self, value):
        return self.converters.get(self.name, lambda v: v)(value)

    @staticmethod
    def to_container(value):
        return value

    @staticmethod
    def to_currency(value):
        return value

    @staticmethod
    def to_date(value):
        return value

    @staticmethod
    def to_datetime(value):
        return value

    @staticmethod
    def to_float(value):
        return value

    @staticmethod
    def to_integer(value):
        return value

    @staticmethod
    def to_string(value):
        return value

    @staticmethod
    def to_time(value):
        return value

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<TypeOf>::%s' % (self.name,)
