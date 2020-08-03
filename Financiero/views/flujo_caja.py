from datetime import datetime

from django.contrib import messages
from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.General import app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaDetalle, SubTipoMovimiento, FlujoCajaEncabezado, EstadoFC, CorteFlujoCaja
from Financiero.models.flujo_caja import EstadoFCDetalle
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorContrato


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
        flujo_caja_enc = FlujoCajaEncabezado.objects.filter(contrato=contrato)
        if flujo_caja_enc:
            flujo_caja_enc = flujo_caja_enc.first()
        else:
            flujo_caja_enc = FlujoCajaEncabezado.objects.create(fecha_crea=datetime.now(), contrato=contrato,
                                                                estado_id=EstadoFC.ALIMENTACION)
            CorteFlujoCaja.objects.create(flujo_caja_enc=flujo_caja_enc)
        if not tiene_permisos_de_acceso(request, contrato.id):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        fecha_minima_mes = obtener_fecha_minima_mes(contrato.id)

        movimientos = FlujoCajaDetalle.objects.filter(flujo_caja_enc__contrato=contrato, tipo_registro=tipo)\
            .annotate(fecha_corte=F('flujo_caja_enc__corteflujocaja__fecha_corte'))\
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)

        if not request.user.has_perms('Financiero.can_access_usuarioespecial'):
            movimientos.exclude(estado_id=EstadoFCDetalle.ELIMINADO)

        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            movimientos = movimientos.filter(subtipo_movimiento__protegido=False)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/detalle_flujo_caja_contratos.html',
                      {'movimientos': movimientos, 'fecha': datetime.now(), 'contrato': contrato, 'tipo': tipo,
                       'menu_actual': 'fc_contratos', 'fecha_minima_mes': fecha_minima_mes,
                       'flujo_caja_enc': flujo_caja_enc})


class FlujoCajaContratosCrearView(AbstractEvaLoggedView):
    def get(self, request, id_contrato, tipo):
        OPCION = 'crear'
        if not tiene_permisos_de_acceso(request, id_contrato):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        if not validar_estado_planeacion_ejecucion(id_contrato, tipo):
            messages.error(request, 'No se puede crear un movimiento porque ya se encuentra en ejecución')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        fecha_minima_mes = obtener_fecha_minima_mes(id_contrato)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-crear-editar.html',
                      datos_xa_render(request, OPCION, id_contrato, tipo, fecha_minima_mes))

    def post(self, request, id_contrato, tipo):
        if not tiene_permisos_de_acceso(request, id_contrato):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        if not validar_estado_planeacion_ejecucion(id_contrato, tipo):
            messages.error(request, 'No se puede crear un movimiento porque ya se encuentra en ejecución')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        fecha_movimiento = request.POST.get('fecha_movimiento', '')
        subtipo_movimiento_id = request.POST.get('subtipo_movimiento_id', '')
        valor = request.POST.get('valor', '')
        flujo_encabezado = FlujoCajaEncabezado.objects.get(contrato_id=id_contrato)
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

        if not tiene_permisos_de_acceso(request, flujo_detalle.flujo_caja_enc.contrato_id) or \
                not validar_gestion_registro(request, flujo_detalle):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        if not validar_estado_planeacion_ejecucion(flujo_detalle.flujo_caja_enc.contrato_id, flujo_detalle.tipo_registro):
            messages.error(request, 'No se puede crear un movimiento porque ya se encuentra en ejecución')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        fecha_minima_mes = obtener_fecha_minima_mes(flujo_detalle.flujo_caja_enc.contrato_id)
        return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-crear-editar.html',
                      datos_xa_render(request, OPCION, flujo_detalle.flujo_caja_enc.contrato_id,
                                      flujo_detalle.tipo_registro, fecha_minima_mes, flujo_detalle=flujo_detalle))

    def post(self, request, id_flujo_caja):
        flujo_detalle = FlujoCajaDetalle.objects.get(id=id_flujo_caja)

        if not tiene_permisos_de_acceso(request, flujo_detalle.flujo_caja_enc.contrato_id) or \
                not validar_gestion_registro(request, flujo_detalle):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse('financiero:flujo-caja-contratos'))

        if not validar_estado_planeacion_ejecucion(flujo_detalle.flujo_caja_enc.contrato_id, flujo_detalle.tipo_registro):
            messages.error(request, 'No se puede crear un movimiento porque ya se encuentra en ejecución')
            return redirect(reverse('financiero:flujo-caja-contratos'))

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

        flujo_detalle = FlujoCajaDetalle.objects.get(id=id)

        if not tiene_permisos_de_acceso(request, flujo_detalle.flujo_caja_enc.contrato_id) or \
                not validar_gestion_registro(request, flujo_detalle):
            return JsonResponse({"estado": "error", "mensaje": "No tiene permisos para acceder a este flujo de caja."})

        if not validar_estado_planeacion_ejecucion(flujo_detalle.flujo_caja_enc.contrato_id, flujo_detalle.tipo_registro):
            return JsonResponse({"estado": "error",
                                 "mensaje": "No se puede crear un movimiento porque ya se encuentra en ejecución"})

        flujo_detalle.estado_id = EstadoFCDetalle.ELIMINADO
        flujo_detalle.comentarios = request.POST['comentarios']
        flujo_detalle.save(update_fields=['comentarios', 'estado'])

        messages.success(request, 'Se ha eliminado el movimiento correctamente')
        return JsonResponse({"estado": "OK"})


# region Métodos de ayuda
def datos_xa_render(request, opcion: str, id_contrato, tipo, fecha_minima_mes,
                    flujo_detalle: FlujoCajaDetalle = None, ) -> dict:
    """
    Datos necesarios para la creación de los html de los Subtipos de Movimientos.
    :param request: request para poder consultar los datos del usuario de sesión.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param id_contrato: Necesario para poder identificar el contrato y el flujo de caja.
    :param tipo: Especifica si es el flujo de caja real o proyectado.
    :param fecha_minima_mes: Dato para validar la fecha minima permitida.
    :param flujo_detalle: Es opcional, se usa para cargar los datos al editar..
    :return: Un diccionario con los datos.
    """
    contrato = Contrato.objects.get(id=id_contrato)
    subtipos_movimientos = valores_select_subtipos_movimientos(request)
    datos = {'opcion': opcion, 'contrato': contrato, 'subtipos_movimientos': subtipos_movimientos, 'tipo': tipo,
             'fecha': app_datetime_now(), 'menu_actual': 'fc_contratos', 'fecha_minima_mes': fecha_minima_mes}
    if flujo_detalle:
        datos['flujo_detalle'] = flujo_detalle
    return datos
# endregion


def tiene_permisos_de_acceso(request, id_contrato):
    if not ColaboradorContrato.objects\
            .filter(contrato_id=id_contrato, colaborador__usuario=request.user):
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            return False
    return True


def validar_gestion_registro(request, flujo_detalle):
    if flujo_detalle.subtipo_movimiento.protegido:
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            return False
    return True


def valores_select_subtipos_movimientos(request):
    subtipos = SubTipoMovimiento.objects.filter(estado=True)
    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        subtipos = subtipos.filter(protegido=False)
    return subtipos.values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')


def obtener_fecha_minima_mes(contrato):
    corte_fc = CorteFlujoCaja.objects.get(flujo_caja_enc__contrato_id=contrato)
    if corte_fc.flujo_caja_enc.estado_id == EstadoFC.ALIMENTACION:
        fecha_minima_mes = '{0}-{1}-1'.format(corte_fc.fecha_corte.year, corte_fc.fecha_corte.month)
    else:
        if datetime.now().date() <= corte_fc.fecha_corte:
            fecha_minima_mes = '{0}-{1}-1'.format(corte_fc.fecha_corte.year, corte_fc.fecha_corte.month - 1)
        else:
            fecha_minima_mes = '{0}-{1}-1'.format(corte_fc.fecha_corte.year, corte_fc.fecha_corte.month)

    fecha_minima_mes = datetime.strptime(fecha_minima_mes, "%Y-%m-%d").date()

    return fecha_minima_mes


REAL = 0
PROYECCION = 1


def validar_estado_planeacion_ejecucion(contrato_id, tipo):
    flujo_enc = FlujoCajaEncabezado.objects.get(contrato_id=contrato_id)
    if tipo == REAL and flujo_enc.estado_id == EstadoFC.EJECUCION or \
            tipo == PROYECCION and flujo_enc.estado_id == EstadoFC.ALIMENTACION:
        return True
    return False
