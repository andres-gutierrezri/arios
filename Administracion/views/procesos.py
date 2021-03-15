from datetime import datetime

from django.shortcuts import render

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaEncabezado


class ProcesosView(AbstractEvaLoggedView):
    def get(self, request):
        procesos = Proceso.objects.values('id', 'nombre', 'objeto')
        flujos_caja = FlujoCajaEncabezado.objects.filter(empresa_id=get_id_empresa_global(request))

        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos, 'fecha': datetime.now(), 'flujos_caja': flujos_caja,
                       'menu_actual': ['procesos', 'flujos_de_caja'],
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})
