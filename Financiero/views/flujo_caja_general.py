import calendar
from datetime import datetime, date

from django.contrib import messages
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.utils import get_id_empresa_global
from Administracion.models import Proceso
from EVA.General import app_datetime_now, app_date_now
from EVA.General.conversiones import add_months, string_to_date, mes_numero_a_letras, obtener_fecha_inicio_de_mes, \
    obtener_fecha_fin_de_mes, fijar_fecha_inicio_mes
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaDetalle, SubTipoMovimiento, FlujoCajaEncabezado, EstadoFlujoCaja, CorteFlujoCaja
from Financiero.models.flujo_caja import EstadoFCDetalle, TipoMovimiento
from Financiero.parametros import ParametrosFinancieros
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorContrato, Colaborador, ColaboradorProceso


class FlujosDeCajaView(AbstractEvaLoggedView):
    def get(self, request, opcion):
        if not validar_permisos(request, 'can_gestion_flujos_de_caja'):
            return redirect(reverse('eva-index'))
        opciones = [{'campo_valor': 0, 'campo_texto': 'Contratos'}, {'campo_valor': 1, 'campo_texto': 'Procesos'}]
        if opcion == 0:
            if request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']) or \
                    request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
                contratos = Contrato.objects.filter(empresa_id=get_id_empresa_global(request))
            else:
                contratos = Contrato.objects.filter(empresa_id=get_id_empresa_global(request),
                                                    colaboradorcontrato__colaborador__usuario=request.user)
            return render(request, 'Financiero/FlujoCaja/FlujoCajaContratos/index.html',
                          {'contratos': contratos, 'fecha': datetime.now(), 'opciones': opciones, 'opcion': opcion,
                           'menu_extendido': 'Financiero/_common/base_financiero.html',
                           'menu_actual': ['flujo_caja', 'flujos_de_caja']})
        else:
            if request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']) or \
                    request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
                procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request))
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


def flujo_caja_detalle(request, tipo, contrato=None, proceso=None, anio_seleccion=None, mes_seleccion=None, ruta=None):
    if proceso:
        ruta_reversa = 'administracion:procesos'
        base_template = 'Administracion/_common/base_administracion.html'
        menu_actual = ['procesos', 'flujos_de_caja']
        proceso = Proceso.objects.get(id=proceso)
        flujo_caja_enc = FlujoCajaEncabezado.objects.filter(proceso=proceso, empresa_id=get_id_empresa_global(request))
        movimientos = FlujoCajaDetalle \
            .objects.filter(flujo_caja_enc__proceso=proceso, tipo_registro=tipo,
                            flujo_caja_enc__empresa_id=get_id_empresa_global(request)) \
            .annotate(fecha_corte=F('flujo_caja_enc__corteflujocaja__fecha_corte')) \
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)
    else:
        ruta_reversa = 'financiero:flujo-caja-contratos'
        base_template = 'Proyectos/_common/base_proyectos.html'
        menu_actual = 'fc_contratos'
        contrato = Contrato.objects.get(id=contrato)
        flujo_caja_enc = FlujoCajaEncabezado.objects.filter(contrato=contrato)
        movimientos = FlujoCajaDetalle \
            .objects.filter(flujo_caja_enc__contrato=contrato, tipo_registro=tipo,
                            flujo_caja_enc__empresa_id=get_id_empresa_global(request)) \
            .annotate(fecha_corte=F('flujo_caja_enc__corteflujocaja__fecha_corte')) \
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)

    eliminados = request.GET.get('eliminados', 'False') == 'True'

    if not request.user.has_perms('Financiero.can_access_usuarioespecial'):
        if not request.user.has_perms(['Financiero.can_gestion_flujos_de_caja']):
            movimientos = movimientos.exclude(estado_id=EstadoFCDetalle.ELIMINADO)

    else:
        if eliminados:
            movimientos = movimientos.exclude(estado_id__in=[EstadoFCDetalle.VIGENTE, EstadoFCDetalle.EDITADO,
                                                             EstadoFCDetalle.APLICADO])
        else:
            movimientos = movimientos.exclude(estado_id__in=[EstadoFCDetalle.ELIMINADO, EstadoFCDetalle.OBSOLETO])

    if flujo_caja_enc:
        flujo_caja_enc = flujo_caja_enc.first()
    else:
        flujo_caja_enc = FlujoCajaEncabezado.objects.create(fecha_crea=datetime.now(), proceso=proceso,
                                                            contrato=contrato,
                                                            estado_id=EstadoFlujoCaja.ALIMENTACION,
                                                            empresa_id=get_id_empresa_global(request))
    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso):
        messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
        return redirect(reverse(ruta_reversa))

    fecha_minima_mes = generar_fecha_minima(tipo)
    fecha_maxima_mes = generar_fecha_maxima(tipo)

    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        movimientos = movimientos.filter(subtipo_movimiento__protegido=False)

    fecha_incial = app_date_now()
    fecha_final = app_date_now()
    if movimientos:
        fecha_incial = fijar_fecha_inicio_mes(movimientos.order_by('fecha_movimiento').first().fecha_movimiento)
        fecha_final = fijar_fecha_inicio_mes(movimientos.order_by('fecha_movimiento').last().fecha_movimiento)

    meses = []
    anios = []
    while fecha_incial <= fecha_final:
        coincidencia_mes = False
        for mes in meses:
            if fecha_incial.month == mes['campo_valor']:
                coincidencia_mes = True
        if not coincidencia_mes:
            meses.append({'campo_valor': fecha_incial.month, 'campo_texto': mes_numero_a_letras(fecha_incial.month)})
        coincidencia_anio = False
        for anio in anios:
            if fecha_incial.year == anio['campo_valor']:
                coincidencia_anio = True
        if not coincidencia_anio:
            anios.append({'campo_valor': fecha_incial.year, 'campo_texto': fecha_incial.year})

        fecha_incial = add_months(fecha_incial, 1)

    coincidencia_mes = False
    for m in meses:
        if m['campo_valor'] == mes_seleccion:
            coincidencia_mes = True

    if not coincidencia_mes:
        mes_seleccion = meses[0]['campo_valor']

    coincidencia_anio = False
    for a in anios:
        if a['campo_valor'] == anio_seleccion:
            coincidencia_anio = True

    if not coincidencia_anio:
        anio_seleccion = anios[0]['campo_valor']

    movimientos = movimientos.filter(
        fecha_movimiento__range=[obtener_fecha_inicio_de_mes(anio_seleccion, mes_seleccion),
                                 obtener_fecha_fin_de_mes(anio_seleccion, mes_seleccion)])\
        .annotate(agrupacion=Concat('subtipo_movimiento__tipo_movimiento__nombre',
                                    Value(' - '),
                                    'subtipo_movimiento__categoria_movimiento__nombre',
                                    output_field=CharField()))
    ingresos = 0
    egresos = 0
    for movimiento in movimientos:
        if movimiento.estado_id != EstadoFCDetalle.ELIMINADO:
            if movimiento.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                ingresos += movimiento.valor
            else:
                egresos += movimiento.valor

    return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/detalle_flujo_caja.html',
                  {'movimientos': movimientos, 'fecha': datetime.now(), 'contrato': contrato, 'proceso': proceso,
                   'menu_actual': menu_actual, 'fecha_minima_mes': fecha_minima_mes, 'tipo': tipo,
                   'fecha_maxima_mes': fecha_maxima_mes, 'flujo_caja_enc': flujo_caja_enc, 'eliminados': eliminados,
                   'base_template': base_template, 'ingresos': ingresos, 'egresos': egresos,
                   'anios': anios, 'meses': meses, 'anio_seleccion': anio_seleccion, 'mes_seleccion': mes_seleccion})


def cargar_modal_crear_editar(request, opcion, tipo=None, contrato=None, proceso=None, movimiento=None):
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
        flujo_encabezado = FlujoCajaEncabezado.objects.get(contrato_id=contrato,
                                                           empresa_id=get_id_empresa_global(request))
    else:
        ruta_reversa = 'administracion:procesos'
        ruta_detalle = 'financiero:flujo-caja-procesos-detalle'
        objeto = proceso
        flujo_encabezado = FlujoCajaEncabezado.objects.get(proceso_id=proceso,
                                                           empresa_id=get_id_empresa_global(request))

    if not tiene_permisos_de_acceso(request, contrato=contrato, proceso=proceso) or \
            not validar_gestion_registro(request, flujo_detalle):
        messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
        return redirect(reverse(ruta_reversa))

    fl_det = FlujoCajaDetalle.from_dictionary(request.POST)
    fl_det.usuario_modifica = request.user
    fl_det.fecha_modifica = app_datetime_now()

    fecha_minima = generar_fecha_minima(tipo)
    if fecha_minima:
        if string_to_date(str(fl_det.fecha_movimiento)) < fecha_minima:
            messages.error(request, 'La fecha ingresada es menor a la fecha mínima permitida')
            return redirect(reverse(ruta_reversa))

    fecha_maxima = generar_fecha_maxima(tipo)
    if fecha_maxima:
        if string_to_date(str(fl_det.fecha_movimiento)) > fecha_maxima:
            messages.error(request, 'La fecha ingresada es mayor a la fecha máxima permitida')
            return redirect(reverse(ruta_reversa))

    if flujo_detalle:
        update_fields = ['fecha_movimiento', 'subtipo_movimiento', 'valor', 'usuario_modifica',
                         'fecha_modifica', 'comentarios', 'estado', 'motivo_edicion']

        motivo_edicion = request.POST.get('motivo', '')
        crear_registro_historial(flujo_detalle, motivo_edicion, EstadoFCDetalle.OBSOLETO)

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
    return redirect(reverse(ruta_detalle, args=[objeto, tipo, string_to_date(str(fl_det.fecha_movimiento)).year,
                                                string_to_date(str(fl_det.fecha_movimiento)).month]))


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
    flujo_detalle.motivo_edicion = request.POST['motivo']
    flujo_detalle.fecha_modifica = app_datetime_now()
    flujo_detalle.save(update_fields=['motivo_edicion', 'estado', 'fecha_modifica'])

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
    historial = historial.annotate(agrupacion=Concat('subtipo_movimiento__tipo_movimiento__nombre',
                                    Value(' - '),
                                    'subtipo_movimiento__categoria_movimiento__nombre',
                                    output_field=CharField()))
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

    subtipos_movimientos = valores_select_subtipos_movimientos(request, contrato, proceso)
    datos = {'opcion': opcion, 'contrato': contrato, 'proceso': proceso, 'subtipos_movimientos': subtipos_movimientos,
             'fecha': app_datetime_now(), 'menu_actual': menu_actual, 'fecha_minima_mes': fecha_minima_mes,
             'tipo': tipo}
    if flujo_detalle:
        datos['flujo_detalle'] = flujo_detalle
    return datos


# endregion


def tiene_permisos_de_acceso(request, contrato=None, proceso=None):
    validacion_adicional =\
        not ColaboradorContrato.objects.filter(contrato_id=contrato, colaborador__usuario=request.user).exists() \
        if contrato else \
        not ColaboradorProceso.objects.filter(proceso_id=proceso, colaborador__usuario=request.user).exists()

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


def valores_select_subtipos_movimientos(request, contrato, proceso):
    subtipos = SubTipoMovimiento.objects.filter(estado=True, solo_contrato=False, solo_proceso=False)
    if contrato:
        subtipos |= SubTipoMovimiento.objects.filter(estado=True, solo_contrato=True)
    if proceso:
        subtipos |= SubTipoMovimiento.objects.filter(estado=True, solo_proceso=True)
    if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
        subtipos = subtipos.filter(protegido=False)
    return subtipos.values(campo_valor=F('id'), campo_texto=F('nombre'))\
        .annotate(agrupacion=Concat('tipo_movimiento__nombre',
                                       Value(' - '),
                                       'categoria_movimiento__nombre',
                                       output_field=CharField())).\
        order_by('agrupacion', 'nombre')


REAL = 0
PROYECCION = 1


def crear_registro_historial(flujo_detalle, motivo_edicion, estado):
    FlujoCajaDetalle.objects \
        .create(fecha_movimiento=flujo_detalle.fecha_movimiento,
                subtipo_movimiento_id=flujo_detalle.subtipo_movimiento_id,
                valor=flujo_detalle.valor, tipo_registro=flujo_detalle.tipo_registro,
                comentarios=flujo_detalle.comentarios,
                usuario_crea=flujo_detalle.usuario_crea, usuario_modifica=flujo_detalle.usuario_modifica,
                flujo_caja_enc=flujo_detalle.flujo_caja_enc, fecha_crea=flujo_detalle.fecha_crea,
                fecha_modifica=app_datetime_now(), flujo_detalle=flujo_detalle,
                estado_id=estado, motivo_edicion=motivo_edicion)


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
        if app_date_now().day <= param_fc.get_corte_ejecucion() != 0:
            fecha_minima = add_months(date(app_date_now().year, app_date_now().month, 1), -1)
        elif param_fc.get_corte_ejecucion() == 0:
            fecha_minima = False
    else:
        if app_date_now().day > param_fc.get_corte_alimentacion() != 0:
            fecha_minima = add_months(date(app_date_now().year, app_date_now().month, 1), 1)
        elif param_fc.get_corte_alimentacion() == 0:
            fecha_minima = False
    return fecha_minima


def generar_fecha_maxima(tipo):
    if tipo == PROYECCION:
        fecha_maxima = False
    else:
        if ParametrosFinancieros.get_params_flujo_caja().get_corte_ejecucion() == 0:
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
    if not fecha_minima:
        return True
    elif flujo_detalle.fecha_movimiento.date() >= fecha_minima:
        return True


class FlujoCajaMovimientoAplicarView(AbstractEvaLoggedView):
    def get(self, request, id_movimiento):
        if not validar_permisos(request, 'change_flujocajadetalle'):
            return redirect(reverse('eva-index'))
        flujo_detalle = FlujoCajaDetalle.objects.get(id=id_movimiento)
        subtipos_movimientos = [{'campo_valor': 1, 'campo_texto': flujo_detalle.subtipo_movimiento.nombre}]
        return render(request, 'Financiero/FlujoCaja/FlujoCajaGeneral/modal-aplicar.html',
                      {'flujo_detalle': flujo_detalle,
                       'subtipos_movimientos': subtipos_movimientos})

    def post(self, request, id_movimiento):
        if not validar_permisos(request, 'change_flujocajadetalle'):
            return redirect(reverse('eva-index'))

        flujo_detalle = FlujoCajaDetalle.objects.get(id=id_movimiento)

        if flujo_detalle.flujo_caja_enc.proceso:
            objeto = flujo_detalle.flujo_caja_enc.proceso_id
            ruta_reversa = 'administracion:procesos'
            ruta_detalle = 'financiero:flujo-caja-procesos-detalle'
        else:
            objeto = flujo_detalle.flujo_caja_enc.contrato_id
            ruta_reversa = 'administracion:contratos'
            ruta_detalle = 'financiero:flujo-caja-contratos-detalle'

        if flujo_detalle.estado_id in [EstadoFCDetalle.ELIMINADO, EstadoFCDetalle.OBSOLETO] or \
                flujo_detalle.tipo_registro != PROYECCION:
            messages.error(request, 'Este movimiento no puede ser aplicado.')
            return redirect(reverse(ruta_reversa))

        if flujo_detalle.estado_id not in [EstadoFCDetalle.VIGENTE, EstadoFCDetalle.EDITADO]:
            messages.error(request, 'Este movimiento ya ha sido aplicado.')
            return redirect(reverse(ruta_reversa))

        if not tiene_permisos_de_acceso(request, proceso=flujo_detalle.flujo_caja_enc.proceso_id,
                                        contrato=flujo_detalle.flujo_caja_enc.contrato_id):
            messages.error(request, 'No tiene permisos para acceder a este flujo de caja.')
            return redirect(reverse(ruta_reversa))

        flujo_detalle.estado_id = EstadoFCDetalle.APLICADO
        flujo_detalle.save(update_fields=['estado'])

        fl_det = FlujoCajaDetalle()
        fl_det.fecha_movimiento = flujo_detalle.fecha_movimiento
        fl_det.subtipo_movimiento = flujo_detalle.subtipo_movimiento
        fl_det.valor = request.POST.get('valor', '')
        fl_det.comentarios = request.POST.get('comentarios', '')
        fl_det.usuario_modifica = request.user
        fl_det.fecha_modifica = app_datetime_now()
        fl_det.tipo_registro = REAL
        fl_det.usuario_crea = request.user
        fl_det.fecha_crea = app_datetime_now()
        fl_det.estado_id = EstadoFCDetalle.APLICADO
        fl_det.flujo_caja_enc = flujo_detalle.flujo_caja_enc
        fl_det.movimiento_proyectado = flujo_detalle
        fl_det.save()
        messages.success(request, 'Se ha aplicado el movimiento correctamente')
        return redirect(reverse(ruta_detalle, args=[objeto, PROYECCION, fl_det.fecha_movimiento.year,
                                                    fl_det.fecha_movimiento.month]))

