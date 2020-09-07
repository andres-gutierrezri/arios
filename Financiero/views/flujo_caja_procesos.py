from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView
from Financiero.views.flujo_caja_general import flujo_caja_detalle, cargar_modal_crear_editar, guardar_movimiento, \
    validar_permisos
from TalentoHumano.models import Colaborador


class FlujoCajaProcesosView(AbstractEvaLoggedView):
    def get(self, request):
        if not validar_permisos(request, 'view_flujocajaencabezado'):
            return redirect(reverse('eva-index'))
        procesos = Proceso.objects.all()
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            colaborador = Colaborador.objects.get(usuario=request.user)
            procesos = procesos.filter(id=colaborador.proceso_id)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                      {'procesos': procesos, 'fecha': datetime.now(), 'menu_actual': 'fc_procesos',
                       'menu_extendido': 'Administracion/_common/base_administracion.html'})


class FlujoCajaProcesosDetalleView(AbstractEvaLoggedView):
    def get(self, request, id, tipo):
        if not validar_permisos(request, 'view_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return flujo_caja_detalle(request, tipo, proceso=id)


class FlujoCajaProcesosCrearView(AbstractEvaLoggedView):
    def get(self, request, id_proceso, tipo):
        OPCION = 'crear'
        if not validar_permisos(request, 'add_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return cargar_modal_crear_editar(request, OPCION, tipo=tipo, proceso=id_proceso)

    def post(self, request, id_proceso, tipo):
        if not validar_permisos(request, 'add_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return guardar_movimiento(request, tipo=tipo, proceso=id_proceso)

