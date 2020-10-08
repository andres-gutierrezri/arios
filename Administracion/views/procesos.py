from datetime import datetime

from django.shortcuts import render

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import Colaborador


class ProcesosView(AbstractEvaLoggedView):
    def get(self, request):
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request))
        proceso_usuario = Colaborador.objects.get(usuario=request.user).proceso
        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos, 'fecha': datetime.now(), 'menu_actual': ['procesos', 'flujos_de_caja'],
                       'proceso_usuario': proceso_usuario,
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})
