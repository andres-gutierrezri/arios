from datetime import datetime

from django.shortcuts import render

from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView


class ProcesosView(AbstractEvaLoggedView):
    def get(self, request):
        procesos = Proceso.objects.all()
        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos, 'fecha': datetime.now(), 'menu_actual': 'procesos',
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})
