from django.db import models


class Rule(models.Model):
    name = models.TextField(verbose_name='name', unique=True, blank=False)
    xpath = models.TextField(verbose_name='xpath', blank=False)
    typeof = models.ForeignKey('TypeOf', on_delete=models.CASCADE)


class TypeOf(models.Model):
    name = models.TextField(verbose_name='name', unique=True, blank=False)
