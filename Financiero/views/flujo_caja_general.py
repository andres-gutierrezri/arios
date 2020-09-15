import calendar
from datetime import datetime, date

from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import Proceso
from Administracion.models.models import Parametro
from EVA.General import app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaDetalle, SubTipoMovimiento, FlujoCajaEncabezado, EstadoFlujoCaja, CorteFlujoCaja
from Financiero.models.flujo_caja import EstadoFCDetalle
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorContrato, Colaborador


CORTE_EJECUCION = Parametro.objects.get_parametro('FINANCIERO', 'FLUJO_CAJA', 'CORTE_EJECUCION').first().id
CORTE_ALIMENTACION = Parametro.objects.get_parametro('FINANCIERO', 'FLUJO_CAJA', 'CORTE_ALIMENTACION').first().id


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
        ruta_reversa = 'financiero:flujo-caja-procesos'
        base_template = 'Administracion/_common/base_administracion.html'
        menu_actual = 'fc_procesos'
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
        CorteFlujoCaja.objects.create(flujo_caja_enc=flujo_caja_enc)
    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso):
        messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
        return redirect(reverse(ruta_reversa))

    fecha_minima_mes = obtener_fecha_minima_mes(contrato=contrato, proceso=proceso)
    fecha_maxima_mes = obtener_fecha_maxima_mes(contrato=contrato, proceso=proceso)

    if not request.user.has_perms('Financiero.can_access_usuarioespecial'):
        if not request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
            movimientos = movimientos.exclude(estado_id=EstadoFCDetalle.ELIMINADO)

    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        movimientos = movimientos.filter(subtipo_movimiento__protegido=False)

    return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/detalle_flujo_caja.html',
                  {'movimientos': movimientos, 'fecha': datetime.now(), 'contrato': contrato, 'proceso': proceso,
                   'menu_actual': menu_actual, 'fecha_minima_mes': fecha_minima_mes, 'tipo': tipo,
                   'fecha_maxima_mes': fecha_maxima_mes, 'flujo_caja_enc': flujo_caja_enc,
                   'base_template': base_template})


def cargar_modal_crear_editar(request,  opcion, tipo=None, contrato=None, proceso=None, movimiento=None):
    if movimiento:
        flujo_detalle = FlujoCajaDetalle.objects.get(id=movimiento)
        contrato = flujo_detalle.flujo_caja_enc.contrato_id
        proceso = flujo_detalle.flujo_caja_enc.proceso_id
        tipo = flujo_detalle.tipo_registro
    else:
        flujo_detalle = None
    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        return JsonResponse({"estado": "error",
                             "mensaje": "No tiene permisos para acceder a este flujo de caja."})

    if not validar_estado_planeacion_ejecucion(tipo, contrato=contrato, proceso=proceso):
        return JsonResponse({"estado": "error",
                             "mensaje": "No se puede crear un movimiento porque ya se encuentra en ejecución"})

    fecha_minima_mes = obtener_fecha_minima_mes(contrato=contrato, proceso=proceso)
    return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-crear-editar.html',
                  datos_xa_render(request, opcion, tipo, fecha_minima_mes, flujo_detalle=flujo_detalle,
                                  contrato=contrato, proceso=proceso))


def guardar_movimiento(request, tipo=None, contrato=None, proceso=None, movimiento=None):
    if movimiento:
        flujo_detalle = FlujoCajaDetalle.objects.get(id=movimiento)
        contrato = flujo_detalle.flujo_caja_enc.contrato_id
        proceso = flujo_detalle.flujo_caja_enc.proceso_id
        tipo = flujo_detalle.tipo_registro
    else:
        flujo_detalle = None
    if contrato:
        ruta_reversa = 'financiero:flujo-caja-contratos'
        ruta_detalle = 'financiero:flujo-caja-contratos-detalle'
        objeto = contrato
        flujo_encabezado = FlujoCajaEncabezado.objects.get(contrato_id=contrato)
    else:
        ruta_reversa = 'financiero:flujo-caja-procesos'
        ruta_detalle = 'financiero:flujo-caja-procesos-detalle'
        objeto = proceso
        flujo_encabezado = FlujoCajaEncabezado.objects.get(proceso_id=proceso)

    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
        return redirect(reverse(ruta_reversa))

    if not validar_estado_planeacion_ejecucion(tipo, contrato=contrato, proceso=proceso):
        messages.error(request, 'No se puede gestionar un movimiento porque ya se encuentra en ejecución')
        return redirect(reverse(ruta_reversa))

    fl_det = FlujoCajaDetalle.from_dictionary(request.POST)
    fl_det.usuario_modifica = request.user
    fl_det.fecha_modifica = app_datetime_now()

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
    tipo = flujo_detalle.tipo_registro

    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        return JsonResponse({"estado": "error", "mensaje": "No tiene permisos para acceder a este flujo de caja."})

    if not validar_estado_planeacion_ejecucion(contrato=contrato, proceso=proceso, tipo=tipo):
        return JsonResponse({"estado": "error",
                             "mensaje": "No se puede crear un movimiento porque ya se encuentra en ejecución"})

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


def obtener_fecha_minima_mes(contrato=None, proceso=None):
    if contrato:
        corte_fc = CorteFlujoCaja.objects.get(flujo_caja_enc__contrato_id=contrato)
    else:
        corte_fc = CorteFlujoCaja.objects.get(flujo_caja_enc__proceso_id=proceso)

    return generar_fecha_minima(corte_fc)


def obtener_fecha_maxima_mes(contrato=None, proceso=None):
    if contrato:
        corte_fc = CorteFlujoCaja.objects.get(flujo_caja_enc__contrato_id=contrato)
    else:
        corte_fc = CorteFlujoCaja.objects.get(flujo_caja_enc__proceso_id=proceso)

    fecha_maxima_mes = validar_corte_flujo_caja(corte_fc)

    return fecha_maxima_mes


REAL = 0
PROYECCION = 1


def validar_estado_planeacion_ejecucion(tipo, contrato=None, proceso=None):
    if contrato:
        flujo_enc = FlujoCajaEncabezado.objects.get(contrato_id=contrato)
    else:
        flujo_enc = FlujoCajaEncabezado.objects.get(proceso_id=proceso)
    if tipo == REAL and flujo_enc.estado_id == EstadoFlujoCaja.EJECUCION or \
            tipo == PROYECCION and flujo_enc.estado_id == EstadoFlujoCaja.ALIMENTACION:
        return True
    return False


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


def validar_corte_flujo_caja(corte_fc):
    corte = CorteFlujoCaja.objects.get(id=corte_fc.id)
    if corte_fc.flujo_caja_enc.estado_id == EstadoFlujoCaja.ALIMENTACION:
        corte.fecha_corte = generar_fecha_corte(CORTE_ALIMENTACION)
    else:
        corte.fecha_corte = generar_fecha_corte_ejecucion(corte)
    corte.save(update_fields=['fecha_corte'])
    return corte.fecha_corte


def generar_fecha_corte(parametro):
    fecha = app_datetime_now()
    dia_corte = int(Parametro.objects.get(id=parametro).valor)
    dia_maximo_mes = (calendar.monthrange(fecha.year, fecha.month))[1]
    if dia_corte > dia_maximo_mes:
        dia_final = dia_maximo_mes
    else:
        dia_final = dia_corte

    anho = fecha.year
    mes = fecha.month

    if parametro == CORTE_EJECUCION:
        if fecha.month == 12:
            anho = fecha.year + 1
            mes = 1
        else:
            mes = fecha.month + 1
    return date(anho, mes, dia_final)


def generar_fecha_minima(flujo_corte):
    fecha = flujo_corte.fecha_corte
    anho = fecha.year
    mes = fecha.month
    if flujo_corte.flujo_caja_enc.estado_id == EstadoFlujoCaja.EJECUCION:
        if fecha.month == 1:
            mes = 12
            anho = fecha.year - 1
        else:
            mes = fecha.month - 1
    return date(anho, mes, 1)


def generar_fecha_corte_ejecucion(corte):
    parametro = Parametro.objects.get(id=CORTE_EJECUCION)
    fecha = corte.fecha_corte
    if int(parametro.valor) != corte.fecha_corte.day:
        fecha_maxima = calendar.monthrange(corte.fecha_corte.year, corte.fecha_corte.month)[1]
        if fecha_maxima > int(parametro.valor):
            dia = int(parametro.valor)
        else:
            dia = fecha_maxima
        fecha_corte_modificada = date(corte.fecha_corte.year, corte.fecha_corte.month, dia)
        if date.today() < fecha_corte_modificada:
            fecha = fecha_corte_modificada
        else:
            fecha = generar_fecha_corte(CORTE_EJECUCION)
    else:
        if app_datetime_now().day > int(parametro.valor):
            if corte.fecha_corte.month == app_datetime_now().month:
                fecha = generar_fecha_corte(CORTE_EJECUCION)
    return fecha

