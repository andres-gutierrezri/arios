from datetime import datetime

from django.shortcuts import render

from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaDetalle
from Proyectos.models import Contrato


class FlujoCajaContratosView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.all()
        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/index.html',
                      {'contratos': contratos, 'fecha': datetime.now(),
                       'menu_actual': 'fc_contratos'})


class FlujoCajaContratosDetalleView(AbstractEvaLoggedView):
    def get(self, request, id, tipo):
        contrato = Contrato.objects.get(id=id)
        flujos_cajas = FlujoCajaDetalle.objects.filter(flujo_caja_enc__contrato=contrato, tipo_registro=tipo)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/detalle_flujo_caja_contratos.html',
                      {'flujos_cajas': flujos_cajas, 'fecha': datetime.now(), 'contrato': contrato, 'tipo': tipo,
                       'menu_actual': 'fc_contratos'})
