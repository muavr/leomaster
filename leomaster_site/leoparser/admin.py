from django import forms
from django.contrib import admin
from leoparser.models import Rule, TypeOf


class RuleAdminForm(forms.ModelForm):
    name = forms.CharField()
    xpath = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}))

    class Meta:
        model = Rule
        fields = ('name', 'xpath', 'typeof', )


class TypeOfAdminForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = TypeOf
        fields = ('name', )


class RuleAdmin(admin.ModelAdmin):
    form = RuleAdminForm
    fields = ('name', 'xpath', 'typeof', 'parent', )
    list_display = ('name', 'xpath', 'typeof', 'parent', )


class TypeOfAdmin(admin.ModelAdmin):
    form = TypeOfAdminForm
    fields = ('name', )
    list_display = ('name', )


admin.site.register(Rule, RuleAdmin)
admin.site.register(TypeOf, TypeOfAdmin)
