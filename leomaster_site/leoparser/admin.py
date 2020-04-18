from django import forms
from django.contrib import admin
from leoparser.models import Parser, Rule, TypeOf


class ParserAdminForm(forms.ModelForm):
    name = forms.CharField()
    rule_set = forms.ModelMultipleChoiceField(queryset=Rule.objects.all(), label='Rules')

    class Meta:
        model = Rule
        fields = ('name', 'rule_set', )


class RuleAdminForm(forms.ModelForm):
    name = forms.CharField()
    xpath = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}))
    regex = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}), required=False)
    sub = forms.CharField(widget=forms.TextInput(attrs={'size': '100'}), required=False)

    class Meta:
        model = Rule
        fields = ('name', 'xpath', 'regex', 'typeof', )


class ParserAdmin(admin.ModelAdmin):
    form = ParserAdminForm
    fields = ('name', 'rule_set', )
    list_display = ('name', )


class RuleAdmin(admin.ModelAdmin):
    form = RuleAdminForm
    fields = ('name', 'xpath', 'regex', 'sub', 'typeof', 'parent', )
    list_display = ('name', 'xpath', 'regex', 'sub', 'typeof', 'parent', )


class TypeOfAdmin(admin.ModelAdmin):
    fields = ('name', )
    list_display = ('name', )


admin.site.register(Parser, ParserAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(TypeOf, TypeOfAdmin)
