from django.db import models
from django.contrib.auth.models import AbstractUser
from leoparser.models import PersistentHistoryDocument


class User(AbstractUser):
    pass


class Location(models.Model):
    name = models.TextField(verbose_name='name', unique=True)
    city = models.TextField(verbose_name='city')
    address = models.TextField(verbose_name='address')
    tz = models.TextField(verbose_name='timezone', default='Europe/Moscow')


class Master(models.Model):
    name = models.TextField(verbose_name='name', unique=True)


class Category(models.Model):
    name = models.TextField(verbose_name='name', unique=True)


class Masterclass(PersistentHistoryDocument):
    date = models.DateTimeField(verbose_name='date', null=True)
    master = models.ForeignKey(Master, verbose_name='master', null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, verbose_name='category', null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, verbose_name='location', null=True, on_delete=models.SET_NULL)
