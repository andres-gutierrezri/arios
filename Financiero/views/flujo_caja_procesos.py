from django.shortcuts import redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from Financiero.views.flujo_caja_general import flujo_caja_detalle, cargar_modal_crear_editar, guardar_movimiento, \
    validar_permisos


class FlujoCajaProcesosDetalleView(AbstractEvaLoggedView):
    def get(self, request, id, tipo, anio, mes):
        if not validar_permisos(request, 'view_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return flujo_caja_detalle(request, tipo, proceso=id, anio_seleccion=anio, mes_seleccion=mes)


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

