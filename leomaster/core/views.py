import pytz

from django.http import Http404
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from datetime import datetime, timedelta

from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

from core.models import Masterclass
from core.serializers import MasterclassSerializer


class MasterclassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Masterclass.objects.all()
    serializer_class = MasterclassSerializer
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        group = self.kwargs.get('group', '')
        tz = pytz.timezone(settings.TIME_ZONE)
        if group == 'topic':
            queryset = Masterclass.objects.all().filter(date__gte=timezone.now()).order_by('-date')
        elif group == 'half_month':
            half_month_ago = datetime.today() - timedelta(days=15)
            half_month_ago = tz.localize(half_month_ago)
            queryset = Masterclass.objects.all().filter(creation_ts__gte=half_month_ago).order_by('-creation_ts')
        elif group == 'month':
            month_ago = datetime.now() - timedelta(days=31)
            month_ago = tz.localize(month_ago)
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
    return render(request, 'core/last_added_masterclasses.html', context=context)

