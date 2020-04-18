from django.contrib import admin

from core.models import Master
from core.models import Location
from core.models import Masterclass


@admin.register(Location)
class MasterAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'city', 'street', 'building', 'tz')
    readonly_fields = ('id',)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    fields = ('id', 'name',)
    readonly_fields = ('id',)


@admin.register(Masterclass)
class MasterclassAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = ('id', 'uid', 'title', 'date', 'price', 'online_price', 'total_seats', 'avail_seats', 'location',
              'master', 'creation_ts', 'modification_ts')
    readonly_fields = ('id', 'creation_ts', 'modification_ts')


