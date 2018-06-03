from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Location(models.Model):
    name = models.CharField(verbose_name='name', max_length=256, unique=True)
    city = models.CharField(verbose_name='city', max_length=256)
    street = models.CharField(verbose_name='street', max_length=256)
    building = models.CharField(verbose_name='building', max_length=256)
    tz = models.CharField(verbose_name='timezone', max_length=256, default='Europe/Moscow')


class Master(models.Model):
    name = models.CharField(verbose_name='name', max_length=256, unique=True)


class Masterclass(models.Model):
    uid = models.CharField(verbose_name='uid', max_length=256, unique=True)
    title = models.CharField(verbose_name='title', max_length=256)
    description = models.TextField(verbose_name='description')
    date = models.DateTimeField(verbose_name='date')
    duration = models.IntegerField(verbose_name='duration', null=True, blank=True)
    age_restriction = models.CharField(verbose_name='age restriction', max_length=256, blank=True)
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name='master')
    total_seats = models.IntegerField(verbose_name='total seats')
    avail_seats = models.IntegerField(verbose_name='available seats')
    price = models.DecimalField(verbose_name='price', max_digits=14, decimal_places=10)
    online_price = models.DecimalField(verbose_name='online price', max_digits=14, decimal_places=10)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='location',)
    max_complexity = models.IntegerField(verbose_name='max complexity')
    complexity = models.IntegerField(verbose_name='complexity')
    preview_img_url = models.URLField(verbose_name='preview image URL')
    img_url = models.URLField(verbose_name='image URL')
    creation_ts = models.DateTimeField('creation timestamp', auto_now_add=True)
    modification_ts = models.DateTimeField('modification timestamp', auto_now=True)
