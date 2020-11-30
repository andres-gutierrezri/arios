import json
from datetime import timedelta
from typing import List, Optional

import requests
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import F
from django.db.transaction import atomic
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse

from Administracion.models import Tercero, Impuesto, ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA import settings
from EVA.General import app_date_now
from EVA.General.conversiones import valor_pesos_a_letras, isostring_to_datetime
from EVA.General.jsonencoders import AriosJSONEncoder
from EVA.General.utilidades import paginar
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FacturaEncabezado, ResolucionFacturacion, FacturaDetalle
from Financiero.models.facturacion import FacturaImpuesto


class FacturasView(AbstractEvaLoggedView):
    def get(self, request):
        page = request.GET.get('page', 1)
        page2 = request.GET.get('page2', 1)
        empresa_id = get_id_empresa_global(request)
        facturas = FacturaEncabezado.objects.filter(empresa_id=empresa_id).exclude(estado=0).order_by('-fecha_creacion',
                                                                                                      '-numero_factura')
        borradores = FacturaEncabezado.objects.filter(estado=0, empresa_id=empresa_id).order_by('-id')

        facturas_page = paginar(facturas, page, 10)
        borradores_page = paginar(borradores, page2, 10)
        borradores_page.nombre_parametro = 'page2'
        return render(request, 'Financiero/Facturacion/Facturas/index.html', {'facturas': facturas_page,
                                                                              'borradores': borradores_page,
                                                                              'menu_actual': 'facturas'})


class FacturaCrearView(AbstractEvaLoggedView):
    def get(self, request):
        terceros = Tercero.objects.clientes_xa_select()
        impuestos = Impuesto.objects.get_xa_select_porcentaje()

        return render(request, 'Financiero/Facturacion/crear_factura.html',
                      {'terceros': terceros, 'impuestos': impuestos, 'menu_actual': 'facturas'})

    def post(self, request):
        resultado = self.guardar_factura(request)
        if resultado['estado'] == 'OK' and 'id_factura' in resultado:
            self.generar_factura_electronica(resultado['id_factura'])

        return JsonResponse(resultado)

    @atomic
    def guardar_factura(self, request) -> dict:
        body_unicode = request.body.decode('utf-8')
        factura = json.loads(body_unicode)

        factura_id = factura['id']
        empresa_id = get_id_empresa_global(request)
        # region Obtiene borrador de factura.
        factura_borrador = None
        if factura_id != 0:
            try:
                factura_borrador = FacturaEncabezado.objects.get(id=factura_id, empresa_id=empresa_id)
            except FacturaEncabezado.DoesNotExist:
                return {'estado': 'error', 'mensaje': 'No se encuentra información del borrador en el sistema'}
        # endregion

        # region Validaciones.
        error_validacion = self.validaciones_factura(factura, factura_borrador)
        if error_validacion:
            return {"estado": "error", "mensaje": error_validacion}
        # endregion

        if factura['estado'] == FacturaEncabezado.Estado.BORRADOR:
            # region Factura encabezado.
            factura_enc = FacturaEncabezado()
            factura_enc.empresa_id = empresa_id
            resolucion = ResolucionFacturacion.objects.filter(empresa_id=factura_enc.empresa_id, estado=True).only('id') \
                .order_by('-fecha_resolucion').first()

            if resolucion is None:
                return {"estado": "error", "mensaje": "No se encontró resolución de facturación"}

            factura_enc.id = factura_id if factura_id != 0 else None
            if factura_enc.id != 0:
                factura_enc.facturadetalle_set.all().delete()
                factura_enc.facturaimpuesto_set.all().delete()
            factura_enc.resolucion_id = resolucion.id
            factura_enc.tercero_id = factura['cliente']
            factura_enc.subtotal = factura['subtotal']
            factura_enc.can_items = factura['cantidadItems']
            factura_enc.valor_impuesto = factura['valorImpuestos']
            factura_enc.base_impuesto = factura['baseImpuestos']
            factura_enc.porcentaje_administracion = factura['porcentajeAdministracion']
            factura_enc.porcentaje_imprevistos = factura['porcentajeImprevistos'] != 0
            factura_enc.porcentaje_utilidad = factura['porcentajeUtilidad']
            factura_enc.amortizacion = factura['amortizacion']
            if factura_enc.amortizacion != 0:
                factura_enc.amortizacion_id = factura['idAmortizacion']
                factura_enc.amortizacion_fecha = isostring_to_datetime(factura['fechaAmortizacion']).date()

            if factura_enc.id:
                factura_enc.usuario_crea_id = factura_borrador.usuario_crea_id
            else:
                factura_enc.usuario_crea_id = request.user.id
            factura_enc.usuario_modifica = request.user
            factura_enc.estado = factura['estado']
            factura_enc.fecha_vencimiento = app_date_now() + timedelta(45)
            factura_enc.fecha_creacion = app_date_now()
            factura_enc.numero_factura = None
            factura_enc.total = factura['total']
            factura_enc.total_letras = valor_pesos_a_letras(factura_enc.total)

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
                factura_det.valor_total = item['valorTotal']
                factura_det.valor_impuesto = item['valorImpuesto']
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
                factura_imp.valor_impuesto = impuesto['valor']

                factura_imp.save()
            # endregion

            return {'estado': 'OK', 'datos': {'factura_id': factura_enc.id}}
        else:
            factura_borrador.estado = FacturaEncabezado.Estado.CREADA
            factura_borrador.numero_factura = ConsecutivoDocumento \
                .get_consecutivo_documento(TipoDocumento.FACTURA, factura_borrador.empresa_id)
            factura_borrador.save(update_fields=['estado', 'numero_factura'])

            return {'estado': 'OK', 'datos': {'factura_numero': factura_borrador.numero_factura},
                    'id_factura': factura_borrador.id}

    @staticmethod
    def validaciones_factura(factura: dict, factura_borrador: FacturaEncabezado) -> Optional[str]:

        # region Valida borrador
        if factura_borrador is not None and factura_borrador.estado != FacturaEncabezado.Estado.BORRADOR:
            return 'Ya no es un borrador de factura y no se puede modificar'
        # endregion

        # region Valida cliente
        try:
            tercero = Tercero.objects.get(id=factura['cliente'])
            mensaje_error = ''
            if factura['estado'] == FacturaEncabezado.Estado.CREADA:
                if tercero.regimen_fiscal is None:
                    mensaje_error += 'Regimen fiscal, '
                if tercero.responsabilidades_fiscales is None:
                    mensaje_error += 'Responsabilidad fiscal, '
                if tercero.tipo_persona is None:
                    mensaje_error += 'Tipo persona, '
                if tercero.tributos is None:
                    mensaje_error += 'Tributos, '
                if tercero.correo_facelec is None:
                    mensaje_error += 'Correo facturación, '
                if tercero.correo_facelec is None:
                    mensaje_error += 'Código postal, '

                if len(mensaje_error) > 0:
                    return 'No se puede crear factura al cliente, le faltan estos datos:\n' + mensaje_error[0:-2]
        except Tercero.DoesNotExist:
            return 'El cliente seleccionado no existe.'
        # endregion

        # region Valida total
        if factura['total'] <= 0:
            return 'El total a pagar debe ser mayor a 0'
        # endregion

        # region Valida AUI y amortización.
        if factura['porcentajeAdministracion'] < 0:
            return 'El porcentaje de administración es inválido'
        if factura['porcentajeImprevistos'] < 0:
            return 'El porcentaje de imprevistos es inválido'
        if factura['porcentajeUtilidad'] < 0:
            return 'El porcentaje de utilidad es inválido'
        if factura['amortizacion'] < 0:
            return 'El valor de amortización es inválido'
        # endregion

        # region Valida ítems
        items: List[dict] = factura['items']
        if len(items) != factura['cantidadItems']:
            return 'La cantidad de ítems reportados no coincide con los ítems recibidos'

        ids_impuestos_items: list = []
        for item in items:
            id_impuesto = item['impuesto']
            if id_impuesto is not None and id_impuesto != 0 and id_impuesto not in ids_impuestos_items:
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

    @staticmethod
    def generar_factura_electronica(id_factura: int):
        response = requests.post(f'{settings.EVA_URL_BASE_FACELEC}{id_factura}/enviar')
        if response.status_code == requests.codes.ok:
            respuesta = response.json()
            if respuesta['estado'] == FacturaEncabezado.Estado.APROBADA_DIAN:
                info_factura = FacturaEncabezado()
                info_factura.id = id_factura
                if FacturaCrearView.enviar_correo(id_factura):
                    info_factura.estado = FacturaEncabezado.Estado.ENVIADA_CLIENTE
                else:
                    info_factura.estado = FacturaEncabezado.Estado.ERROR_ENVIADO_CORREO

                info_factura.save(update_fields=['estado'])

    @staticmethod
    def enviar_correo(id_factura: int) -> bool:

        try:
            info_factura = FacturaEncabezado.objects.\
                values('resolucion__prefijo', 'numero_factura', 'empresa__nombre', 'empresa__nit', 'tercero__nombre',
                       'tercero__correo_facelec', 'nombre_archivo_ad', 'cufe').get(id=id_factura)

            asunto = f"{info_factura['empresa__nit']}; {info_factura['empresa__nombre']}; " \
                     f"{info_factura['resolucion__prefijo']}{info_factura['numero_factura']}; 01; " \
                     f"{info_factura['empresa__nombre']}"

            from_email = '"Facturación {}" <noreply@arios-ing.com>'.format(info_factura['empresa__nombre'])

            ruta_adjunto = f"{settings.EVA_RUTA_ARCHIVOS_FACTURA}{info_factura['empresa__nit']}/" \
                           f"{info_factura['nombre_archivo_ad'].replace('xml', 'zip')}"

            plantilla = get_template('Financiero/Facturacion/Facturas/correo.html')

            email = EmailMessage(asunto,  plantilla.render(info_factura), from_email,
                                 [info_factura['tercero__correo_facelec']],
                                 ['contaduria@arios-ing.com'])
            email.attach_file(ruta_adjunto)
            email.content_subtype = "html"
            valor = email.send()
            print(valor)
        except:
            return False

        return True


class FacturaEditarView(AbstractEvaLoggedView):
    def get(self, request, id_factura):
        try:
            terceros = Tercero.objects.clientes_xa_select()
            impuestos = Impuesto.objects.get_xa_select_porcentaje()
            factura = FacturaEncabezado.objects.get(id=id_factura, empresa_id=get_id_empresa_global(request))
        except FacturaEncabezado.DoesNotExist:
            messages.error(self.request, 'No se encontró el borrador de factura solicitado.')
            return redirect(reverse('Financiero:factura-index'))

        return render(request, 'Financiero/Facturacion/crear_factura.html',
                      {'terceros': terceros, 'impuestos': impuestos, 'factura': factura, 'menu_actual': 'facturas'})


class FacturaDetalleView(AbstractEvaLoggedView):
    def get(self, request, id_factura):
        try:
            factura = FacturaEncabezado.objects.\
                values('id', 'estado', 'subtotal', 'amortizacion', 'total', cliente=F('tercero_id'),
                       fechaVencimiento=F('fecha_vencimiento'), cantidadItems=F('can_items'),
                       numeroFactura=F('numero_factura'), valorImpuestos=F('valor_impuesto'),
                       baseImpuestos=F('base_impuesto'),
                       porcentajeAdministracion=F('porcentaje_administracion'),
                       porcentajeImprevistos=F('porcentaje_imprevistos'), porcentajeUtilidad=F('porcentaje_utilidad'),)\
                .get(id=id_factura, empresa_id=get_id_empresa_global(request))

            items_factura = list(FacturaDetalle.objects
                                 .values('titulo', 'descripcion', 'cantidad', 'impuesto',
                                         valorUnitario=F('valor_unitario'), valorTotal=F('valor_total'),
                                         valorImpuesto=F('valor_impuesto'))
                                 .filter(factura_encabezado_id=id_factura))

            impuestos_factura = list(FacturaImpuesto.objects
                                     .values('impuesto', porcentaje=F('impuesto__porcentaje'),
                                             nombre=F('impuesto__nombre'), base=F('valor_base'),
                                             valor=F('valor_impuesto'))
                                     .filter(factura_encabezado_id=id_factura))

            for impuesto in impuestos_factura:
                impuesto['id'] = impuesto.pop('impuesto')

            factura['items'] = items_factura
            factura['impuestos'] = impuestos_factura

            return JsonResponse({'estado': 'OK', 'datos': factura}, encoder=AriosJSONEncoder)

        except FacturaEncabezado.DoesNotExist:
            return JsonResponse({"estado": "error", "mensaje": 'La factura no existe.'})


class FacturaImprimirView(AbstractEvaLoggedView):
    def get(self, request, id_factura):
        try:
            factura = FacturaEncabezado.objects.get(id=id_factura, empresa_id=get_id_empresa_global(request))
            if factura.nombre_archivo_ad:
                ruta_adjunto = f"{settings.EVA_RUTA_ARCHIVOS_FACTURA}{factura.empresa.nit}/" \
                               f"{factura.nombre_archivo_ad.replace('xml', 'pdf')}"
                return FileResponse(open(ruta_adjunto, 'rb'), filename="factura {0}.pdf".format(factura.id))
            else:
                messages.error(self.request, 'No se encontró la representación grafica para la factura.')
                return redirect(reverse('Financiero:factura-index'))
        except FacturaEncabezado.DoesNotExist:
            messages.error(self.request, 'No se encontró la factura solicitada.')
            return redirect(reverse('Financiero:factura-index'))


class FacturaEnviarCorreo(AbstractEvaLoggedView):

    def get(self, request, id_factura):
        if FacturaCrearView.enviar_correo(id_factura):
            return JsonResponse({"estado": "OK", "mensaje": 'Factura enviada al cliente'})
        else:
            return JsonResponse({"estado": "error", "mensaje": 'La factura no existe.'})


