from django.shortcuts import render
from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView


class Index(AbstractEvaLoggedView):
        def get(self, request):
            procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
            return render(request, 'SGI/index.html', {'procesos': procesos})
