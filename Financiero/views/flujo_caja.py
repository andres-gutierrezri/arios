from datetime import datetime
import pytz

from django.contrib import messages
from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.General import app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaDetalle, SubTipoMovimiento, FlujoCajaEncabezado, EstadoFC, CorteFlujoCaja
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorContrato
utc = pytz.UTC


class FlujoCajaContratosView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.all()
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            contratos = contratos.filter(colaboradorcontrato__colaborador__usuario=request.user)

        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/index.html',
                      {'contratos': contratos, 'fecha': datetime.now(),
                       'menu_actual': 'fc_contratos'})


class FlujoCajaContratosDetalleView(AbstractEvaLoggedView):
    def get(self, request, id, tipo):
        contrato = Contrato.objects.get(id=id)
        validar_permisos_de_acceso(request, contrato.id)
        fecha_corte = CorteFlujoCaja.objects.get(flujo_caja_enc__contrato=contrato).fecha_corte

        if datetime.strptime('2020-08-10', "%Y-%m-%d").date() <= fecha_corte.date():
            fecha_minima_mes = '{0}-{1}-1'.format(fecha_corte.year, fecha_corte.month - 1)
        else:
            fecha_minima_mes = '{0}-{1}-1'.format(fecha_corte.year, fecha_corte.month)
        fecha_minima_mes = datetime.strptime(fecha_minima_mes, "%Y-%m-%d").date()

        movimientos = FlujoCajaDetalle.objects.filter(flujo_caja_enc__contrato=contrato, tipo_registro=tipo)\
            .annotate(estado=F('flujo_caja_enc__estado'), fecha_corte=F('flujo_caja_enc__corteflujocaja__fecha_corte'))

        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            movimientos = movimientos.filter(subtipo_movimiento__protegido=False)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/detalle_flujo_caja_contratos.html',
                      {'movimientos': movimientos, 'fecha': datetime.now(), 'contrato': contrato, 'tipo': tipo,
                       'menu_actual': 'fc_contratos', 'fecha_minima_mes': fecha_minima_mes})


class FlujoCajaContratosCrearView(AbstractEvaLoggedView):
    def get(self, request, id_contrato, tipo):
        OPCION = 'crear'
        validar_permisos_de_acceso(request, id_contrato)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-crear-editar.html',
                      datos_xa_render(OPCION, id_contrato, tipo))

    def post(self, request, id_contrato, tipo):
        validar_permisos_de_acceso(request, id_contrato)
        fecha_movimiento = request.POST.get('fecha_movimiento', '')
        subtipo_movimiento_id = request.POST.get('subtipo_movimiento_id', '')
        valor = request.POST.get('valor', '')
        flujos_encabezados = FlujoCajaEncabezado.objects\
            .filter(contrato_id=id_contrato, finalizado_fecha_corte=False)
        if flujos_encabezados:
            flujo_encabezado = flujos_encabezados.first()
        else:
            flujo_encabezado = FlujoCajaEncabezado.objects.create(contrato_id=id_contrato, estado_id=EstadoFC.NUEVO,
                                                                  fecha_crea=app_datetime_now(),
                                                                  finalizado_fecha_corte=False)
        FlujoCajaDetalle.objects\
            .create(fecha_movimiento=fecha_movimiento, subtipo_movimiento_id=subtipo_movimiento_id,
                    valor=valor, tipo_registro=tipo, usuario_crea=request.user, usuario_modifica=request.user,
                    flujo_caja_enc=flujo_encabezado, fecha_crea=app_datetime_now(), fecha_modifica=app_datetime_now())

        messages.success(request, 'Se ha agregado el movimiento correctamente')
        return redirect(reverse('financiero:flujo-caja-contratos-detalle', args=[id_contrato, tipo]))


class FlujoCajaContratosEditarView(AbstractEvaLoggedView):
    def get(self, request, id_flujo_caja):
        OPCION = 'editar'
        flujo_detalle = FlujoCajaDetalle.objects.get(id=id_flujo_caja)
        validar_permisos_de_acceso(request, flujo_detalle.flujo_caja_enc.contrato_id)
        validar_gestion_registro(request, flujo_detalle)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-crear-editar.html',
                      datos_xa_render(OPCION, flujo_detalle.flujo_caja_enc.contrato_id, flujo_detalle.tipo_registro,
                                      flujo_detalle=flujo_detalle))

    def post(self, request, id_flujo_caja):
        flujo_detalle = FlujoCajaDetalle.objects.get(id=id_flujo_caja)
        validar_permisos_de_acceso(request, flujo_detalle.flujo_caja_enc.contrato_id)
        validar_gestion_registro(request, flujo_detalle)
        flujo_detalle.fecha_movimiento = request.POST.get('fecha_movimiento', '')
        flujo_detalle.subtipo_movimiento_id = request.POST.get('subtipo_movimiento_id', '')
        flujo_detalle.valor = request.POST.get('valor', '')
        flujo_detalle.fecha_modifica = app_datetime_now()
        flujo_detalle.save(update_fields=['fecha_movimiento', 'subtipo_movimiento', 'valor', 'fecha_modifica'])

        messages.success(request, 'Se ha editado el movimiento correctamente')
        return redirect(reverse('financiero:flujo-caja-contratos-detalle',
                                args=[flujo_detalle.flujo_caja_enc.contrato_id, flujo_detalle.tipo_registro]))


class FlujoCajaContratosEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            flujo_detalle = FlujoCajaDetalle.objects.get(id=id)
            validar_permisos_de_acceso(request, flujo_detalle.flujo_caja_enc.contrato_id)
            validar_gestion_registro(request, flujo_detalle)
            flujo_detalle.delete()
            messages.success(request, 'Se ha eliminado el movimiento correctamente')
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error", "mensaje": "Este movimiento no puede ser eliminado"
                                                               "porque ya fue el flujo de caja ya fue cerrado."})


# region Métodos de ayuda
def datos_xa_render(opcion: str, id_contrato, tipo, flujo_detalle: FlujoCajaDetalle = None) -> dict:
    """
    Datos necesarios para la creación de los html de los Subtipos de Movimientos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param sub_mov: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """
    contrato = Contrato.objects.get(id=id_contrato)
    subtipos_movimientos = SubTipoMovimiento.objects.get_xa_select_activos()
    datos = {'opcion': opcion, 'contrato': contrato, 'subtipos_movimientos': subtipos_movimientos, 'tipo': tipo,
             'fecha': app_datetime_now(), 'menu_actual': 'fc_contratos'}
    if flujo_detalle:
        datos['flujo_detalle'] = flujo_detalle

    return datos
# endregion


def validar_permisos_de_acceso(request, id_contrato):
    if not ColaboradorContrato.objects\
            .filter(contrato_id=id_contrato, colaborador__usuario=request.user):
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))
    return True


def validar_gestion_registro(request, flujo_detalle):
    if flujo_detalle.subtipo_movimiento.protegido:
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))

    return True


def valores_select_subtipos_movimientos(request):
    subtipos = SubTipoMovimiento.objects.filter(estado=True)
    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        subtipos = subtipos.filter(protegido=False)
    return subtipos.values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')


def obtener_fecha_minima_mes(contrato):
    fecha_corte = CorteFlujoCaja.objects.get(flujo_caja_enc__contrato_id=contrato).fecha_corte

    if datetime.strptime('2020-08-10', "%Y-%m-%d").date() <= fecha_corte.date():
        fecha_minima_mes = '{0}-{1}-1'.format(fecha_corte.year, fecha_corte.month - 1)
    else:
        fecha_minima_mes = '{0}-{1}-1'.format(fecha_corte.year, fecha_corte.month)
    fecha_minima_mes = datetime.strptime(fecha_minima_mes, "%Y-%m-%d").date()

    return fecha_minima_mes
