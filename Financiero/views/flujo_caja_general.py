import calendar
from datetime import datetime, date

from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import Proceso
from EVA.General import app_datetime_now, app_date_now
from EVA.General.conversiones import add_months, string_to_date
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaDetalle, SubTipoMovimiento, FlujoCajaEncabezado, EstadoFlujoCaja, CorteFlujoCaja
from Financiero.models.flujo_caja import EstadoFCDetalle, TipoMovimiento
from Financiero.parametros import ParametrosFinancieros
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorContrato, Colaborador


class FlujosDeCajaView(AbstractEvaLoggedView):
    def get(self, request, opcion):
        if not validar_permisos(request, 'can_gestion_flujos_de_caja'):
            return redirect(reverse('eva-index'))
        opciones = [{'campo_valor': 0, 'campo_texto': 'Contratos'}, {'campo_valor': 1, 'campo_texto': 'Procesos'}]
        if opcion == 0:
            if request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']) or \
                    request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
                contratos = Contrato.objects.all()
            else:
                contratos = Contrato.objects.filter(colaboradorcontrato__colaborador__usuario=request.user)
            return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/index.html',
                          {'contratos': contratos, 'fecha': datetime.now(), 'opciones': opciones, 'opcion': opcion,
                           'menu_extendido': 'Financiero/_common/base_financiero.html',
                           'menu_actual': ['flujo_caja', 'flujos_de_caja']})
        else:
            if request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']) or \
                    request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
                procesos = Proceso.objects.all()
            else:
                colaborador = Colaborador.objects.get(usuario=request.user)
                procesos = Proceso.objects.filter(id=colaborador.proceso_id)
            return render(request, 'Financiero/FlujoCaja/FlujoCajaProcesos/index.html',
                          {'procesos': procesos, 'fecha': datetime.now(), 'opciones': opciones, 'opcion': opcion,
                           'menu_extendido': 'Financiero/_common/base_financiero.html',
                           'menu_actual': ['flujo_caja', 'flujos_de_caja']})


class FlujoCajaMovimientoEditarView(AbstractEvaLoggedView):
    def get(self, request, id_movimiento):
        OPCION = 'editar'
        if not validar_permisos(request, 'change_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return cargar_modal_crear_editar(request, OPCION, movimiento=id_movimiento)

    def post(self, request, id_movimiento):
        if not validar_permisos(request, 'change_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return guardar_movimiento(request, movimiento=id_movimiento)


class FlujoCajaMovimientoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id_movimiento):
        if not validar_permisos(request, 'delete_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        return eliminar_movimiento(request, flujo_detalle=id_movimiento)


class FlujoCajaMovimientoHistorialView(AbstractEvaLoggedView):
    def get(self, request, id_movimiento):
        if not validar_permisos(request, 'can_gestion_flujos_de_caja'):
            return redirect(reverse('eva-index'))
        return historial_movimiento(request, id_movimiento)


def flujo_caja_detalle(request, tipo, contrato=None, proceso=None):
    if proceso:
        ruta_reversa = 'administracion:procesos'
        base_template = 'Administracion/_common/base_administracion.html'
        menu_actual = ['procesos', 'flujos_de_caja']
        proceso = Proceso.objects.get(id=proceso)
        flujo_caja_enc = FlujoCajaEncabezado.objects.filter(proceso=proceso)
        movimientos = FlujoCajaDetalle.objects.filter(flujo_caja_enc__proceso=proceso, tipo_registro=tipo) \
            .annotate(fecha_corte=F('flujo_caja_enc__corteflujocaja__fecha_corte')) \
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)
    else:
        ruta_reversa = 'financiero:flujo-caja-contratos'
        base_template = 'Proyectos/_common/base_proyectos.html'
        menu_actual = 'fc_contratos'
        contrato = Contrato.objects.get(id=contrato)
        flujo_caja_enc = FlujoCajaEncabezado.objects.filter(contrato=contrato)
        movimientos = FlujoCajaDetalle.objects.filter(flujo_caja_enc__contrato=contrato, tipo_registro=tipo) \
            .annotate(fecha_corte=F('flujo_caja_enc__corteflujocaja__fecha_corte')) \
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)

    if flujo_caja_enc:
        flujo_caja_enc = flujo_caja_enc.first()
    else:
        flujo_caja_enc = FlujoCajaEncabezado.objects.create(fecha_crea=datetime.now(), proceso=proceso, contrato=contrato,
                                                            estado_id=EstadoFlujoCaja.ALIMENTACION)
    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso):
        messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
        return redirect(reverse(ruta_reversa))

    fecha_minima_mes = generar_fecha_minima(tipo)
    fecha_maxima_mes = generar_fecha_maxima(tipo)

    if not request.user.has_perms('Financiero.can_access_usuarioespecial'):
        if not request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
            movimientos = movimientos.exclude(estado_id=EstadoFCDetalle.ELIMINADO)

    ingresos = 0
    egresos = 0
    for movimiento in movimientos:
        if movimiento.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
            ingresos += movimiento.valor
        else:
            egresos += movimiento.valor

    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        movimientos = movimientos.filter(subtipo_movimiento__protegido=False)

    return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/detalle_flujo_caja.html',
                  {'movimientos': movimientos, 'fecha': datetime.now(), 'contrato': contrato, 'proceso': proceso,
                   'menu_actual': menu_actual, 'fecha_minima_mes': fecha_minima_mes, 'tipo': tipo,
                   'fecha_maxima_mes': fecha_maxima_mes, 'flujo_caja_enc': flujo_caja_enc,
                   'base_template': base_template, 'ingresos': ingresos, 'egresos': egresos})


def cargar_modal_crear_editar(request,  opcion, tipo=None, contrato=None, proceso=None, movimiento=None):
    if movimiento:
        flujo_detalle = FlujoCajaDetalle.objects.get(id=movimiento)
        contrato = flujo_detalle.flujo_caja_enc.contrato_id
        proceso = flujo_detalle.flujo_caja_enc.proceso_id
        tipo = flujo_detalle.tipo_registro

        if not validar_fecha_accion(flujo_detalle):
            return JsonResponse({"estado": "error",
                                 "mensaje": "No tiene permisos para realizar esta acción."})
    else:
        flujo_detalle = None
    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        return JsonResponse({"estado": "error",
                             "mensaje": "No tiene permisos para acceder a este flujo de caja."})

    fecha_minima_mes = generar_fecha_minima(tipo)
    return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-crear-editar.html',
                  datos_xa_render(request, opcion, tipo, fecha_minima_mes, flujo_detalle=flujo_detalle,
                                  contrato=contrato, proceso=proceso))


def guardar_movimiento(request, tipo=None, contrato=None, proceso=None, movimiento=None):
    if movimiento:
        flujo_detalle = FlujoCajaDetalle.objects.get(id=movimiento)
        contrato = flujo_detalle.flujo_caja_enc.contrato_id
        proceso = flujo_detalle.flujo_caja_enc.proceso_id
        tipo = flujo_detalle.tipo_registro

        if not validar_fecha_accion(flujo_detalle):
            return JsonResponse({"estado": "error",
                                 "mensaje": "No tiene permisos para realizar esta acción."})
    else:
        flujo_detalle = None
    if contrato:
        ruta_reversa = 'financiero:flujo-caja-contratos'
        ruta_detalle = 'financiero:flujo-caja-contratos-detalle'
        objeto = contrato
        flujo_encabezado = FlujoCajaEncabezado.objects.get(contrato_id=contrato)
    else:
        ruta_reversa = 'administracion:procesos'
        ruta_detalle = 'financiero:flujo-caja-procesos-detalle'
        objeto = proceso
        flujo_encabezado = FlujoCajaEncabezado.objects.get(proceso_id=proceso)

    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
        return redirect(reverse(ruta_reversa))

    fl_det = FlujoCajaDetalle.from_dictionary(request.POST)
    fl_det.usuario_modifica = request.user
    fl_det.fecha_modifica = app_datetime_now()

    if string_to_date(str(fl_det.fecha_movimiento)) < generar_fecha_minima(tipo):
        messages.error(request, 'La fecha ingresada es menor a la fecha mínima permitida')
        return redirect(reverse(ruta_reversa))

    fecha_maxima = generar_fecha_maxima(tipo)
    if fecha_maxima:
        if string_to_date(str(fl_det.fecha_movimiento)) > fecha_maxima:
            messages.error(request, 'La fecha ingresada es mayor a la fecha máxima permitida')
            return redirect(reverse(ruta_reversa))

    if flujo_detalle:
        update_fields = ['fecha_movimiento', 'subtipo_movimiento', 'valor', 'usuario_modifica',
                         'fecha_modifica', 'comentarios', 'estado']

        comentarios = request.POST.get('comentarios', '')
        crear_registro_historial(flujo_detalle, comentarios, EstadoFCDetalle.OBSOLETO)

        fl_det.id = flujo_detalle.id
        fl_det.estado_id = EstadoFCDetalle.EDITADO
        fl_det.save(update_fields=update_fields)
        messages.success(request, 'Se ha editado el movimiento correctamente')
    else:
        fl_det.tipo_registro = tipo
        fl_det.usuario_crea = request.user
        fl_det.fecha_crea = app_datetime_now()
        fl_det.estado_id = EstadoFCDetalle.VIGENTE
        fl_det.flujo_caja_enc = flujo_encabezado
        fl_det.save()
        messages.success(request, 'Se ha agregado el movimiento correctamente')

    return redirect(reverse(ruta_detalle, args=[objeto, tipo]))


def eliminar_movimiento(request, flujo_detalle):
    flujo_detalle = FlujoCajaDetalle.objects.get(id=flujo_detalle)
    contrato = flujo_detalle.flujo_caja_enc.contrato_id
    proceso = flujo_detalle.flujo_caja_enc.proceso_id

    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        return JsonResponse({"estado": "error", "mensaje": "No tiene permisos para acceder a este flujo de caja."})

    if not validar_fecha_accion(flujo_detalle):
        return JsonResponse({"estado": "error",
                             "mensaje": "No tiene permisos para realizar esta acción."})

    flujo_detalle.estado_id = EstadoFCDetalle.ELIMINADO
    flujo_detalle.comentarios = request.POST['comentarios']
    flujo_detalle.fecha_modifica = app_datetime_now()
    flujo_detalle.save(update_fields=['comentarios', 'estado', 'fecha_modifica'])

    messages.success(request, 'Se ha eliminado el movimiento correctamente')
    return JsonResponse({"estado": "OK"})


def historial_movimiento(request, movimiento):
    flujo_detalle = FlujoCajaDetalle.objects.filter(id=movimiento)
    contrato = flujo_detalle.first().flujo_caja_enc.contrato_id
    proceso = flujo_detalle.first().flujo_caja_enc.proceso_id

    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle.first()):
        messages.error(request, 'No tiene permisos para acceder a este historial de flujo de caja.')
        return redirect(reverse('financiero:flujo-caja-movimiento'))

    historial = FlujoCajaDetalle.objects.filter(flujo_detalle=flujo_detalle.first())
    historial |= flujo_detalle
    return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-historial.html',
                  {'historial': historial})


# region Métodos de ayuda
def datos_xa_render(request, opcion: str, tipo, fecha_minima_mes, flujo_detalle: FlujoCajaDetalle = None,
                    contrato=None, proceso=None) -> dict:
    """
    Datos necesarios para la creación de los html de los Subtipos de Movimientos.
    :param request: request para poder consultar los datos del usuario de sesión.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param tipo: Especifica si es el flujo de caja real o proyectado.
    :param fecha_minima_mes: Dato para validar la fecha minima permitida.
    :param flujo_detalle: Es opcional, se usa para cargar los datos al editar.
    :param contrato: Necesario para poder identificar el contrato y el flujo de caja.
    :param proceso: Necesario para poder identificar el proceso y el flujo de caja.
    :return: Un diccionario con los datos.
    """
    if contrato:
        contrato = Contrato.objects.get(id=contrato)
        menu_actual = 'fc_contratos'
    else:
        proceso = Proceso.objects.get(id=proceso)
        menu_actual = 'fc_procesos'

    subtipos_movimientos = valores_select_subtipos_movimientos(request)
    datos = {'opcion': opcion, 'contrato': contrato, 'proceso': proceso, 'subtipos_movimientos': subtipos_movimientos,
             'fecha': app_datetime_now(), 'menu_actual': menu_actual, 'fecha_minima_mes': fecha_minima_mes,
             'tipo': tipo}
    if flujo_detalle:
        datos['flujo_detalle'] = flujo_detalle
    return datos
# endregion


def tiene_permisos_de_acceso(request, contrato=None, proceso=None):
    validacion_adicional = False
    if contrato:
        if not ColaboradorContrato.objects\
                .filter(contrato_id=contrato, colaborador__usuario=request.user):
            validacion_adicional = True
    else:
        if not Colaborador.objects.filter(proceso_id=proceso, usuario=request.user):
            validacion_adicional = True
    if validacion_adicional:
        if request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
            return True
        elif request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            return True
        else:
            return False
    return True


def validar_gestion_registro(request, flujo_detalle):
    if flujo_detalle and flujo_detalle.subtipo_movimiento.protegido:
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            return False
    return True


def valores_select_subtipos_movimientos(request):
    subtipos = SubTipoMovimiento.objects.filter(estado=True)
    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        subtipos = subtipos.filter(protegido=False)
    return subtipos.values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')


REAL = 0
PROYECCION = 1


def crear_registro_historial(flujo_detalle, comentarios, estado):
    FlujoCajaDetalle.objects \
        .create(fecha_movimiento=flujo_detalle.fecha_movimiento,
                subtipo_movimiento_id=flujo_detalle.subtipo_movimiento_id,
                valor=flujo_detalle.valor, tipo_registro=flujo_detalle.tipo_registro,
                usuario_crea=flujo_detalle.usuario_crea, usuario_modifica=flujo_detalle.usuario_modifica,
                flujo_caja_enc=flujo_detalle.flujo_caja_enc, fecha_crea=flujo_detalle.fecha_crea,
                fecha_modifica=app_datetime_now(), flujo_detalle=flujo_detalle,
                estado_id=estado, comentarios=comentarios)


def validar_permisos(request, permiso):
    if permiso == 'can_gestion_flujos_de_caja':
        permiso = 'Financiero.can_gestion_flujos_de_caja'
    else:
        permiso = 'Financiero.{0}'.format(permiso)
    if not request.user.has_perm(permiso):
        messages.error(request, 'No tiene permisos para acceder a esta funcionalidad')
        return False
    else:
        return True


def generar_fecha_minima(tipo):
    fecha_minima = date(app_date_now().year, app_date_now().month, 1)
    param_fc = ParametrosFinancieros.get_params_flujo_caja()
    if tipo == REAL:
        if app_date_now().day <= param_fc.get_corte_ejecucion():
            fecha_minima = add_months(date(app_date_now().year, app_date_now().month, 1), -1)
    else:
        if app_date_now().day > param_fc.get_corte_alimentacion():
            fecha_minima = add_months(date(app_date_now().year, app_date_now().month, 1), 1)
    return fecha_minima


def generar_fecha_maxima(tipo):
    if tipo == PROYECCION:
        fecha_maxima = False
    else:
        fecha_maxima = app_date_now()
    return fecha_maxima


def obtener_dia_maximo(parametro):
    dia_maximo = calendar.monthrange(app_date_now().year, app_date_now().month)[1]
    dia_parametro = int(parametro.valor)
    dia = dia_parametro
    if dia_parametro > dia_maximo:
        dia = dia_maximo
    return dia


def validar_fecha_accion(flujo_detalle):
    fecha_minima = generar_fecha_minima(flujo_detalle.tipo_registro)
    if flujo_detalle.fecha_movimiento.date() >= fecha_minima:
        return True



