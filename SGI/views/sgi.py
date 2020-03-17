from django.shortcuts import render, redirect, reverse
from Administracion.models import Proceso
from EVA.General.validacionpermisos import tiene_permisos
from EVA.views.index import AbstractEvaLoggedView

# Create your views here.


class Index(AbstractEvaLoggedView):
        def get(self, request):
            if not tiene_permisos(request, 'SGI', None, None):
                return redirect(reverse('eva-index'))
            else:
                procesos = Proceso.objects.all()
                return render(request, 'SGI/index.html', {'procesos': procesos})
