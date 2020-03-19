from django.shortcuts import render, redirect, reverse
from Administracion.models import Proceso
from EVA.General.validacionpermisos import tiene_permisos
from EVA.views.index import AbstractEvaLoggedView

# Create your views here.


class Index(AbstractEvaLoggedView):
        def get(self, request):
            procesos = Proceso.objects.all()
            return render(request, 'SGI/index.html', {'procesos': procesos})
