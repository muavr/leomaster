import pytz

from django.http import Http404
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from datetime import datetime, timedelta

from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

from leomaster_app.models import Masterclass
from leomaster_app.serializers import MasterclassSerializer


class MasterclassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Masterclass.objects.all()
    serializer_class = MasterclassSerializer
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        group = self.kwargs.get('group', '')
        if group == 'topic':
            queryset = Masterclass.objects.all().filter(date__gte=timezone.now()).order_by('-date')
        elif group == 'half_month':
            half_month_ago = datetime.today() - timedelta(days=15)
            half_month_ago = half_month_ago.astimezone(pytz.timezone(settings.TIME_ZONE))
            queryset = Masterclass.objects.all().filter(creation_ts__gte=half_month_ago).order_by('-creation_ts')
        elif group == 'month':
            month_ago = datetime.now() - timedelta(days=31)
            month_ago = month_ago.astimezone(pytz.timezone(settings.TIME_ZONE))
            queryset = Masterclass.objects.all().filter(creation_ts__gte=month_ago).order_by('-creation_ts')
        elif group == 'all':
            queryset = Masterclass.objects.all().order_by('-date')
        else:
            queryset = Masterclass.objects.all()
        return queryset


def show_masterclasses(request, group):
    available_groups = ['topic', 'half_month', 'month', 'all']
    if group not in available_groups:
        raise Http404
    context = {
        'group': group
    }
    return render(request, 'leomaster_app/last_added_masterclasses.html', context=context)

