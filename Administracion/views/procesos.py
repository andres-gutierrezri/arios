from datetime import datetime

from django.db.models import OuterRef, Exists, F
from django.shortcuts import render

from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models.colaboradores import ColaboradorProceso


class ProcesosView(AbstractEvaLoggedView):
    def get(self, request):

        procesos_usuario = ColaboradorProceso.objects\
            .filter(colaborador__usuario=request.user, proceso_id=OuterRef('pk'))

        procesos = Proceso.objects\
            .values('id', 'nombre', 'objeto', estado_fc=F('flujocajaencabezado__estado__nombre'))\
            .annotate(proceso_usuario=Exists(procesos_usuario))

        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos, 'fecha': datetime.now(),
                       'menu_actual': ['procesos', 'flujos_de_caja'],
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})
