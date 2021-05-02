from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Financiero.views.flujo_caja_general import flujo_caja_detalle, cargar_modal_crear_editar, guardar_movimiento, \
    validar_permisos
from Proyectos.models import Contrato


class FlujoCajaContratosView(AbstractEvaLoggedView):
    def get(self, request):
        if not validar_permisos(request, 'view_flujocajaencabezado'):
            return redirect(reverse('eva-index'))

        contratos = Contrato.objects.filter(empresa_id=get_id_empresa_global(request))
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            contratos = contratos.filter(colaboradorcontrato__colaborador__usuario=request.user)

        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/index.html',
                      {'contratos': contratos, 'fecha': datetime.now(), 'menu_actual': 'fc_contratos',
                       'menu_extendido': 'Proyectos/_common/base_proyectos.html'})


class FlujoCajaContratosDetalleView(AbstractEvaLoggedView):
    def get(self, request, id, tipo, anio, mes):
        if not validar_permisos(request, 'view_flujocajadetalle'):
            return redirect(reverse('eva-index'))

        return flujo_caja_detalle(request, tipo, contrato=id, anio_seleccion=anio, mes_seleccion=mes,
                                  ruta='Financiero:flujo-caja-contratos')


class FlujoCajaContratosCrearView(AbstractEvaLoggedView):
    def get(self, request, id_contrato, tipo):
        OPCION = 'crear'
        if not validar_permisos(request, 'add_flujocajadetalle'):
            return redirect(reverse('eva-index'))

        return cargar_modal_crear_editar(request, OPCION, tipo=tipo, contrato=id_contrato)

    def post(self, request, id_contrato, tipo):
        if not validar_permisos(request, 'add_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return guardar_movimiento(request, tipo=tipo, contrato=id_contrato)

