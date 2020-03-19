from django.shortcuts import render, redirect, reverse

from EVA.General.validacionpermisos import tiene_permisos
from EVA.views.index import AbstractEvaLoggedView
from django.contrib import messages

# Create your views here.


class Index(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'TalentoHumano/index.html')
