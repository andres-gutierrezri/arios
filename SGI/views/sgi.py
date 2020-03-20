from django.shortcuts import render
from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView


class Index(AbstractEvaLoggedView):
        def get(self, request):
            procesos = Proceso.objects.filter(empresa_id=request.session['empresa']['id'])
            return render(request, 'SGI/index.html', {'procesos': procesos})
