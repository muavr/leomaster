# -*- coding: utf-8 -*-
import time
from django import template

register = template.Library()


@register.filter
def repeat(value, arg):
    return str(value) * arg


@register.filter
def mul(value, arg):
    if isinstance(value, int):
        return value * arg
    return len(str(value)) * arg


@register.filter
def idiv(value, arg):
    if isinstance(value, int):
        return value // arg
    return len(str(value)) // arg


@register.filter('time')
def seconds_to_time(seconds):
    return time.strftime('%H {0} %M {1}', time.gmtime(seconds)).format('ч.', 'мин.')


@register.filter
def split_by(l, n=6):
    return [l[i:i+n] for i in range(0, len(l), n)]



