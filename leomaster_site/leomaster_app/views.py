from django.shortcuts import render
from leomaster_app.models import Masterclass
from django.utils import timezone
from django.http import Http404
from datetime import datetime, timedelta


def show_masterclasses(request, group):
    available_groups = ['topic', 'half_month', 'month', 'all']
    if group not in available_groups:
        raise Http404

    if group == 'topic':
        queryset = Masterclass.objects.all().filter(date__gte=timezone.now()).order_by('-date')
    elif group == 'half_month':
        half_month_ago = datetime.today() - timedelta(days=15)
        queryset = Masterclass.objects.all().filter(creation_ts__gte=half_month_ago).order_by('-creation_ts')
    elif group == 'month':
        month_ago = datetime.today() - timedelta(days=31)
        queryset = Masterclass.objects.all().filter(creation_ts__gte=month_ago).order_by('-creation_ts')
    elif group == 'all':
        queryset = Masterclass.objects.all().order_by('-date')
    else:
        queryset = Masterclass.objects.all()

    context = {
        'masterclasses': queryset,
        'group': group
    }
    return render(request, 'leomaster_app/last_added_masterclasses.html', context=context)

