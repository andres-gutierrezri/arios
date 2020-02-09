from datetime import datetime
import json
from typing import List, Optional

from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import render

from Administracion.models import Tercero, Impuesto, ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FacturaEncabezado, ResolucionFacturacion, FacturaDetalle
from Financiero.models.facturacion import FacturaImpuesto


class FacturasView(AbstractEvaLoggedView):
    def get(self, request):
        facturas = FacturaEncabezado.objects.exclude(estado=0)
        borradores = FacturaEncabezado.objects.filter(estado=0)
        return render(request, 'Financiero/Facturacion/facturas/index.html', {'facturas': facturas,
                                                                              'borradores': borradores})


class FacturaCrearView(AbstractEvaLoggedView):
    def get(self, request):

        terceros = Tercero.objects.clientes_xa_select()
        impuestos = Impuesto.objects.get_xa_select_porcentaje()

        return render(request, 'Financiero/Facturacion/crear_factura.html',
                      {'terceros': terceros, 'impuestos': impuestos})

    @atomic
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        factura = json.loads(body_unicode)

        factura_id = factura['id']

        # region Obtiene borrador de factura.
        factura_borrador = None
        if factura_id != 0:
            try:
                factura_borrador = FacturaEncabezado.objects.get(id=factura_id)
            except FacturaEncabezado.DoesNotExist:
                return JsonResponse({'estado': 'error',
                                     'mensaje': 'No se encuentra información del borrador en el sistema'})
        # endregion

        # region Validaciones.
        error_validacion = self.validaciones_factura(factura, factura_borrador)
        if error_validacion:
            return JsonResponse({"estado": "error", "mensaje": error_validacion})
        # endregion

        if factura['estado'] == 0:
            # region Factura encabezado.
            factura_enc = FacturaEncabezado()
            factura_enc.empresa_id = get_id_empresa_global(request)
            resolucion = ResolucionFacturacion.objects.filter(empresa_id=factura_enc.empresa_id, estado=True).only('id')\
                .order_by('-fecha_resolucion').first()

            if resolucion is None:
                return JsonResponse({"estado": "error", "mensaje": "No se encontró resolución de facturación"})

            factura_enc.id = factura_id if factura_id != 0 else None
            if factura_enc.id != 0:
                factura_enc.facturadetalle_set.all().delete()
                factura_enc.facturaimpuesto_set.all().delete()
            factura_enc.resolucion_id = resolucion.id
            factura_enc.tercero_id = factura['cliente']
            factura_enc.subtotal = factura['subtotal']
            factura_enc.can_items = factura['cantidadItems']
            factura_enc.valor_impuesto = factura['valorImpuestos']
            if factura['porcentajeAdministracion'] > 0:
                factura_enc.porcentaje_administracion = factura['porcentajeAdministracion']
            if factura['porcentajeImprevistos'] > 0:
                factura_enc.porcentaje_imprevistos = factura['porcentajeImprevistos'] != 0
            if factura['porcentajeUtilidad'] > 0:
                factura_enc.porcentaje_utilidad = factura['porcentajeUtilidad']
            if factura['amortizacion'] > 0:
                factura_enc.amortizacion = factura['amortizacion']
            if factura_enc.id:
                factura_enc.usuario_crea_id = factura_borrador.usuario_crea_id
            else:
                factura_enc.usuario_crea_id = request.user.id
            factura_enc.usuario_modifica = request.user
            factura_enc.estado = factura['estado']
            factura_enc.fecha_vencimiento = datetime.now()
            factura_enc.fecha_creacion = datetime.now()
            factura_enc.numero_factura = None
            factura_enc.total = factura['total']

            factura_enc.save()
            factura['id'] = factura_enc.id
            # endregion

            # region Factura detalle.
            items: List[dict] = factura['items']
            for item in items:
                factura_det = FacturaDetalle()
                factura_det.factura_encabezado_id = factura_enc.id
                factura_det.titulo = item['titulo']
                factura_det.descripcion = item['descripcion']
                factura_det.valor_unitario = item['valorUnitario']
                factura_det.cantidad = item['cantidad']
                if item['impuesto'] != 0:
                    factura_det.impuesto_id = item['impuesto']

                factura_det.save()
            # endregion

            # region Factura impuestos.
            impuestos: List[dict] = factura['impuestos']
            for impuesto in impuestos:
                if impuesto['base'] == 0:
                    continue
                factura_imp = FacturaImpuesto()
                factura_imp.factura_encabezado_id = factura_enc.id
                factura_imp.impuesto_id = impuesto['id']
                factura_imp.valor_base = impuesto['base']

                factura_imp.save()
            # endregion

            return JsonResponse({'estado': 'OK', 'datos': {'factura_id': factura_enc.id}})
        else:
            factura_borrador.estado = 1
            factura_borrador.numero_factura = ConsecutivoDocumento\
                .get_consecutivo_documento(TipoDocumento.FACTURA, factura_borrador.empresa_id)
            factura_borrador.save(update_fields=['estado', 'numero_factura'])

            return JsonResponse({'estado': 'OK', 'datos': {'factura_numero': factura_borrador.numero_factura}})

    @staticmethod
    def validaciones_factura(factura: dict, factura_borrador: FacturaEncabezado) -> Optional[str]:

        # region Valida borrador
        if factura_borrador is not None and factura_borrador.estado != 0:
            return 'Ya no es un borrador de factura y no se puede modificar'
        # endregion

        # region Valida cliente
        try:
            Tercero.objects.get(id=factura['cliente'])
        except Tercero.DoesNotExist:
            return 'El cliente seleccionado no existe.'
        # endregion

        # region Valida total
        if factura['total'] <= 0:
            return 'El total a pagar debe ser mayor a 0'
        # endregion

        # region Valida ítems
        items: List[dict] = factura['items']
        if len(items) != factura['cantidadItems']:
            return 'La cantidad de ítems reportados no coincide con los ítems recibidos'

        ids_impuestos_items: list = []
        for item in items:
            id_impuesto = item['impuesto']
            if id_impuesto != 0 and id_impuesto not in ids_impuestos_items:
                ids_impuestos_items.append(id_impuesto)

        if Impuesto.objects.filter(id__in=ids_impuestos_items).count() != len(ids_impuestos_items):
            return 'Uno o varios de los impuestos aplicados no existen'
        # endregion

        # region Valida impuestos
        impuestos: List[dict] = factura['impuestos']
        ids_impuestos: list = []

        for impuesto in impuestos:
            id_impuesto = impuesto['id']
            if id_impuesto != 0 and id_impuesto not in ids_impuestos:
                ids_impuestos.append(id_impuesto)

        if Impuesto.objects.filter(id__in=ids_impuestos).count() != len(ids_impuestos):
            return 'Uno o varios de los impuestos reportados no existen'
        # endregion

        return None
