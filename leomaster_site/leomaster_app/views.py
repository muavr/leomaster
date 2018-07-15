from django.shortcuts import render
from leomaster_app.models import Masterclass


def show_last_added_masterclasses(request):
    queryset = Masterclass.objects.all().order_by('-date')
    context = {
        'masterclasses': queryset
    }
    return render(request, 'leomaster_app/last_added_masterclasses.html', context=context)
