from django.contrib import admin

from core.models import Master
from core.models import Category
from core.models import Location
from core.models import Masterclass


@admin.register(Location)
class LocationAdminModel(admin.ModelAdmin):
    fields = ('id', 'name', 'city', 'street', 'building', 'tz', )
    readonly_fields = ('id', )


@admin.register(Master)
class MasterAdminModel(admin.ModelAdmin):
    fields = ('id', 'name', )
    readonly_fields = ('id', )


@admin.register(Category)
class CategoryAdminModel(admin.ModelAdmin):
    fields = ('id', 'name', )
    readonly_fields = ('id', )


@admin.register(Masterclass)
class MasterclassAdminModel(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = ('uid', 'category', 'content', 'location', 'master', )


