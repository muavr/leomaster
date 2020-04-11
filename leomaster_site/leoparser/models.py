import re
import json
import uuid
from django.db import models
from dictdiffer import diff, patch
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist


class Rule(models.Model):
    name = models.TextField(verbose_name='name', blank=False)
    xpath = models.TextField(verbose_name='xpath', blank=False)
    regex = models.TextField(verbose_name='regex', blank=True)
    sub = models.TextField(verbose_name='sub', blank=True)
    typeof = models.ForeignKey('TypeOf', on_delete=models.CASCADE)
    parent = models.ForeignKey('Rule', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('name', )
        unique_together = ('name', 'parent',)

    @property
    def caption(self):
        return self.title or self.name

    def apply(self, element):
        res = element.xpath(self.xpath)
        if self.regex:
            regex = re.compile(self.regex, re.UNICODE | re.IGNORECASE)
            extracted = regex.search(res)
            res = extracted.group(0) if extracted else res
            if self.sub:
                res = regex.sub(self.sub, res)
        return self.typeof.convert(res)

    def __str__(self):
        return '%s::%s(%s)' % (self.typeof, self.name, self.xpath)

    def __repr__(self):
        return '<%s: id="%s" body="%s">' % (self.__class__.__name__, self.id, self.__str__(),)

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'xpath': self.xpath,
                'type': self.typeof.name,
                'parent': self.parent.id if self.parent else None,
                'children': [c.id for c in self.children.all()]}


def apply_once_or_many(f):
    def wrapper(value):
        if isinstance(value, (list, tuple)):
            if len(value) > 1:
                return [f(v) for v in value]
            elif len(value) == 1:
                value = value[0]
        return f(value)
    return wrapper


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
        ordering = ('name',)

    def convert(self, value):
        return self.converters.get(self.name, lambda v: v)(value)

    @staticmethod
    @apply_once_or_many
    def to_container(value):
        return value

    @staticmethod
    @apply_once_or_many
    def to_currency(value):
        return value

    @staticmethod
    @apply_once_or_many
    def to_date(value):
        return value

    @staticmethod
    @apply_once_or_many
    def to_datetime(value):
        return value

    @staticmethod
    @apply_once_or_many
    def to_float(value):
        return float(value)

    @staticmethod
    @apply_once_or_many
    def to_integer(value):
        return int(value)

    @staticmethod
    @apply_once_or_many
    def to_string(value):
        return str(value).strip()

    @staticmethod
    @apply_once_or_many
    def to_time(value):
        return value

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s: id="%s" name="%s">' % (self.__class__.__name__, self.id, self.__str__(),)


class DocDelta(models.Model):
    base = models.ForeignKey('GenericDocument', related_name='delta_set', null=False, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    delta = JSONField(default=list)

    def __str__(self):
        return json.dumps(self.delta, indent=1)

    def __repr__(self):
        return '<%s: id="%s" delta="%s">' % (self.__class__.__name__, self.id, self.delta,)


class HistoryManager(models.Manager):

    def __init__(self, unique_field='uid', *args, **kwargs):
        self.unique_field = unique_field
        super().__init__(*args, **kwargs)

    def save(self, content, *args, **kwargs):
        try:
            unique_value = str(content.pop(self.unique_field))
        except KeyError:
            unique_value = uuid.uuid4().hex

        lookup = {self.unique_field: unique_value}
        try:

            doc = self.get_queryset().get(**lookup)
            doc.content = content
            delta = doc.delta
            doc.save(*args, **kwargs)
            is_new = False
        except ObjectDoesNotExist:
            doc = self.get_queryset().create(content=content, **lookup)
            delta = doc.delta
            is_new = True

        return doc, is_new, delta


class GenericDocument(models.Model):
    uid = models.TextField(unique=True)
    content = JSONField(default=dict, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    _track_change = False
    _track_add = False
    _track_remove = False

    objects = models.Manager()
    history = HistoryManager()

    def __init__(self, *args, **kwargs):
        self._old_content = None
        super().__init__(*args, **kwargs)

    @property
    def actions(self):
        actions = []
        if self._track_change:
            actions.append('change')
        if self._track_add:
            actions.append('add')
        if self._track_remove:
            actions.append('remove')
        return actions

    def __setattr__(self, key, value):
        if key == 'content':
            # instance has already created
            if self.__dict__.get('id') and self._old_content is None:
                self._old_content = self.__dict__.get('content')
        return super().__setattr__(key, value)

    @property
    def patched_content(self):
        if self._old_content is None:
            return self.content
        return patch(self.delta, self._old_content)

    def save(self, *args, **kwargs):
        if self._old_content is not None:
            super().__setattr__('content', self.patched_content)
        super().save(*args, **kwargs)
        self._old_content = None

    @property
    def delta(self):
        if self._old_content is not None:
            return self._gen_delta(self._old_content, self.content)
        return list()

    def _gen_delta(self, original, modified):
        for action in diff(original, modified):
            if action[0] in self.actions:
                yield action

    def __str__(self):
        return '%s%s' % (json.dumps(self.content)[:100], '...')

    def __repr__(self):
        return '<%s: id="%s" uid="%s">' % (self.__class__.__name__, self.id, self.uid,)


class TrackChangeMixin:
    _track_change = True


class TrackAddMixin:
    _track_add = True


class TrackRemoveMixin:
    _track_remove = True


class PersistentHistoryDocument(TrackChangeMixin, TrackAddMixin, GenericDocument):
    """
    Only updates and additional information are tracked
    All deletions will be ignored
    """

    class Meta:
        proxy = True


class UnsteadyHistoryDocument(TrackChangeMixin, TrackAddMixin, TrackRemoveMixin, GenericDocument):
    """
    All changes (add, updates and deletion) will be counted
    """

    class Meta:
        proxy = True


class Document(PersistentHistoryDocument):
    pass


class RemovableHistoryDocument(UnsteadyHistoryDocument):
    pass
