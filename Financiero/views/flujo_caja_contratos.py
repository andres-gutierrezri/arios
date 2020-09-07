from datetime import datetime

from django.shortcuts import render

from EVA.views.index import AbstractEvaLoggedView
from Financiero.views.flujo_caja_general import flujo_caja_detalle, cargar_modal_crear_editar, guardar_movimiento
from Proyectos.models import Contrato


class FlujoCajaContratosView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.all()
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            contratos = contratos.filter(colaboradorcontrato__colaborador__usuario=request.user)

        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/index.html',
                      {'contratos': contratos, 'fecha': datetime.now(), 'menu_actual': 'fc_contratos',
                       'menu_extendido': 'Proyectos/_common/base_proyectos.html'})


class FlujoCajaContratosDetalleView(AbstractEvaLoggedView):
    def get(self, request, id, tipo):
        return flujo_caja_detalle(request, tipo, contrato=id)


class FlujoCajaContratosCrearView(AbstractEvaLoggedView):
    def get(self, request, id_contrato, tipo):
        OPCION = 'crear'
        return cargar_modal_crear_editar(request, OPCION, tipo=tipo, contrato=id_contrato)

    def post(self, request, id_contrato, tipo):
        return guardar_movimiento(request, tipo=tipo, contrato=id_contrato)

