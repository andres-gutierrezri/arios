from datetime import datetime

from django.db.models import OuterRef, Exists
from django.shortcuts import render

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaEncabezado
from TalentoHumano.models.colaboradores import ColaboradorProceso


class ProcesosView(AbstractEvaLoggedView):
    def get(self, request):
        proceso_usuario = ColaboradorProceso.objects\
            .filter(colaborador__usuario=request.user, proceso_id=OuterRef('pk'))
        procesos = Proceso.objects.values('id', 'nombre', 'objeto')\
            .annotate(proceso_usuario=Exists(proceso_usuario))
        flujos_caja = FlujoCajaEncabezado.objects.filter(empresa_id=get_id_empresa_global(request))
        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos, 'fecha': datetime.now(), 'flujos_caja': flujos_caja,
                       'menu_actual': ['procesos', 'flujos_de_caja'],
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})
