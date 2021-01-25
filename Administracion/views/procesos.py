from datetime import datetime

from django.shortcuts import render

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaEncabezado
from TalentoHumano.models.colaboradores import ColaboradorProceso


class ProcesosView(AbstractEvaLoggedView):
    def get(self, request):
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request))
        procesos_usuario = ColaboradorProceso.objects.filter(colaborador__usuario=request.user)

        procesos_lista = []
        for pro in procesos:
            proceso_usuario = False
            for pro_us in procesos_usuario:
                if pro == pro_us.proceso:
                    proceso_usuario = True
            procesos_lista.append({'id': pro.id,
                                   'nombre': pro.nombre,
                                   'objeto': pro.objeto,
                                   'proceso_usuario': proceso_usuario,
                                   'flujocajaencabezado_set':
                                       {'first': {'estado':
                                                  FlujoCajaEncabezado.objects.filter(proceso=pro).first().estado}}})
        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos_lista, 'fecha': datetime.now(),
                       'menu_actual': ['procesos', 'flujos_de_caja'],
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})
