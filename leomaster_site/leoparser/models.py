from django.db import models


class Rule(models.Model):
    name = models.TextField(verbose_name='name', unique=True, blank=False)
    xpath = models.TextField(verbose_name='xpath', blank=False)
    typeof = models.ForeignKey('TypeOf', on_delete=models.CASCADE)
    parent = models.ForeignKey('Rule', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return '%s::%s::%s' % (self.name, self.xpath, self.typeof)

    def __repr__(self):
        return '<Rule>::%s' % (self.name,)


class TypeOf(models.Model):
    name = models.TextField(verbose_name='name', unique=True, blank=False)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<TypeOf>::%s' % (self.name,)
