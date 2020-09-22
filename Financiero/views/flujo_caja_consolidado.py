import json
from datetime import datetime

from django.contrib import messages
from django.db.models import F
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.General import app_date_now
from EVA.General.conversiones import obtener_fecha_fin_de_mes, obtener_fecha_inicio_de_mes, sumar_meses, \
    mes_numero_a_letras
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaEncabezado
from Financiero.models.flujo_caja import SubTipoMovimiento, FlujoCajaDetalle, EstadoFCDetalle, CategoriaMovimiento, \
    TipoMovimiento

COMPARATIVO = 2
REAL = 0


class FlujoCajaConsolidadoView(AbstractEvaLoggedView):
    def get(self, request):
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            return redirect(reverse('eva-index'))
        return render(request, 'Financiero/FlujoCaja/FlujoCajaConsolidado/index.html', datos_xa_render())

    def post(self, request):
        if not request.user.has_perms(['TalentoHumano.can_access_usuarioespecial']):
            return redirect(reverse('eva-index'))
        datos = datos_formulario_consolidado(request)
        if datos['fecha_desde']:
            fecha_desde = datos['fecha_desde']
        else:
            fecha_desde = datos['fecha_min']

        if datos['fecha_hasta']:
            fecha_hasta = datos['fecha_hasta']
        else:
            fecha_hasta = datos['fecha_max']

        tipos_flujos_caja = [0, 1]
        if datos['tipos_flujos_caja'] != '':
            if datos['tipos_flujos_caja'] != 2:
                tipos_flujos_caja = [datos['tipos_flujos_caja']]

        if datos['estados']:
            estados = datos['estados']
        else:
            estados = [1, 2, 4]

        if datos['subtipos']:
            subtipos = datos['subtipos']
        else:
            subtipos = SubTipoMovimiento.objects.all()

        if datos['categorias']:
            categorias = datos['categorias']
        else:
            categorias = CategoriaMovimiento.objects.all()

        con_pro = []
        if datos['lista_contratos']:
            for valor in datos['lista_contratos']:
                con_pro.append(valor)
        else:
            for valor in FlujoCajaEncabezado.objects.get_flujos_x_contrato():
                con_pro.append(valor.id)

        if datos['lista_procesos']:
            for valor in datos['lista_procesos']:
                con_pro.append(valor)
        else:
            for valor in FlujoCajaEncabezado.objects.get_flujos_x_proceso():
                con_pro.append(valor.id)

        movimientos = FlujoCajaDetalle.objects\
            .filter(estado_id__in=estados, flujo_caja_enc__in=con_pro,
                    fecha_movimiento__range=[fecha_desde, fecha_hasta], tipo_registro__in=tipos_flujos_caja,
                    subtipo_movimiento_id__in=subtipos,
                    subtipo_movimiento__categoria_movimiento__in=categorias)\
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)

        if not movimientos:
            messages.warning(request, 'No se encontraron concidencias')
        return render(request, 'Financiero/FlujoCaja/FlujoCajaConsolidado/index.html',
                      datos_xa_render(datos, movimientos))


def datos_xa_render(datos_formulario=None, movimientos=None):
    procesos_contratos = FlujoCajaDetalle.objects.all().order_by('fecha_movimiento')
    if procesos_contratos:
        fecha_min = procesos_contratos.first().fecha_movimiento
        fecha_max = procesos_contratos.last().fecha_movimiento
    else:
        fecha_min = ''
        fecha_max = ''

    fecha_min_max = json.dumps({'fecha_min': str(fecha_min),
                                'fecha_max': str(fecha_max)})

    procesos = FlujoCajaEncabezado.objects.get_xa_select_x_proceso()
    contratos = FlujoCajaEncabezado.objects.get_xa_select_x_contrato()

    subtipos = SubTipoMovimiento.objects.get_xa_select_activos()
    categorias = CategoriaMovimiento.objects.get_xa_select_activos()
    subtipos_categorias = []
    for sub in SubTipoMovimiento.objects.all():
        subtipos_categorias.append({'id': sub.id, 'nombre': sub.nombre, 'categoria_id': sub.categoria_movimiento_id})

    tipos_flujos = [{'campo_valor': 1, 'campo_texto': 'Proyectado'},
                    {'campo_valor': 2, 'campo_texto': 'Comparativo'}]

    estados = [{'campo_valor': 1, 'campo_texto': 'Vigente'},
               {'campo_valor': 2, 'campo_texto': 'Editado'},
               {'campo_valor': 4, 'campo_texto': 'Eliminado'}]

    datos = {'procesos': procesos, 'contratos': contratos, 'tipos_flujos': tipos_flujos, 'estados': estados,
             'categorias': categorias, 'subtipos': subtipos, 'fecha_actual': datetime.today(),
             'subtipos_categorias': json.dumps(subtipos_categorias), 'fecha_min_max': fecha_min_max,
             'menu_actual': ['flujo_caja', 'consolidado']}

    quitar_selecciones = {'texto': 'Quitar Selecciones', 'icono': 'fa-times'}
    seleccionar_todos = {'texto': 'Seleccionar Todos', 'icono': 'fa-check'}
    datos['textos_contratos'] = seleccionar_todos
    datos['textos_procesos'] = seleccionar_todos
    datos['textos_subtipos'] = seleccionar_todos
    datos['textos_categorias'] = seleccionar_todos

    if datos_formulario:
        datos['valor'] = datos_formulario

        if datos_formulario['lista_contratos']:
            datos['textos_contratos'] = quitar_selecciones

        if datos_formulario['lista_procesos']:
            datos['textos_procesos'] = quitar_selecciones

        if datos_formulario['subtipos']:
            datos['textos_subtipos'] = quitar_selecciones

        if datos_formulario['categorias']:
            datos['textos_categorias'] = quitar_selecciones

        if datos_formulario['tipos_flujos_caja'] == COMPARATIVO:
            datos['comparativo'] = True

    else:
        datos['valor'] = {'estados': [1, 2]}

    if movimientos:
        consolidado = construir_consolidado(movimientos)
        datos['movimientos'] = consolidado['lista_categorias']
        datos['totales'] = consolidado['totales']
        datos['meses'] = consolidado['lista_meses']

    return datos


def datos_formulario_consolidado(request):
    procesos = request.POST.getlist('proceso[]', [])
    contratos = request.POST.getlist('contrato[]', [])
    fecha_desde = request.POST.get('fecha_desde', '')
    fecha_hasta = request.POST.get('fecha_hasta', '')
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")

    categorias = request.POST.getlist('categorias[]', [])
    subtipos = request.POST.getlist('subtipos[]', [])
    tipos_flujos_caja = request.POST.get('tipos_flujos_caja_id', '')
    estados = request.POST.getlist('estados[]', [])

    lista_procesos = []
    for pro in procesos:
        lista_procesos.append(int(pro))

    lista_contratos = []
    for con in contratos:
        lista_contratos.append(int(con))

    if estados:
        lista_estados = []
        for y in estados:
            lista_estados.append(int(y))
    else:
        lista_estados = [1, 2]

    lista_subtipos = []
    for z in subtipos:
        lista_subtipos.append(int(z))

    lista_categorias = []
    for cat in categorias:
        lista_categorias.append(int(cat))

    if tipos_flujos_caja:
        tipos_flujos_caja = int(tipos_flujos_caja)

    movimientos = FlujoCajaDetalle.objects.all().order_by('fecha_movimiento')
    if movimientos:
        fecha_min = movimientos.first().fecha_movimiento
        fecha_max = movimientos.last().fecha_movimiento
    else:
        fecha_min = datetime.now()
        fecha_max = datetime.now()
    return {'lista_procesos': lista_procesos, 'lista_contratos': lista_contratos, 'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta, 'subtipos': lista_subtipos, 'tipos_flujos_caja': tipos_flujos_caja,
            'estados': lista_estados, 'fecha_min': fecha_min, 'fecha_max': fecha_max, 'categorias': lista_categorias}


def obtener_fecha_minima(objeto):
    primera_fecha = app_date_now()
    for x in objeto:
        if x.fecha_movimiento.date() < primera_fecha:
            primera_fecha = x.fecha_movimiento.date()
    return obtener_fecha_inicio_de_mes(primera_fecha.year, primera_fecha.month)


def obtener_fecha_maxima(objeto):
    segunda_fecha = app_date_now()
    for x in objeto:
        if x.fecha_movimiento.date() > segunda_fecha:
            segunda_fecha = x.fecha_movimiento.date()
    return segunda_fecha


def construir_consolidado(objeto):
    fecha_minima = obtener_fecha_minima(objeto)
    fecha_maxima = obtener_fecha_maxima(objeto)

    categorias = objeto.distinct('subtipo_movimiento__categoria_movimiento')\
        .values(id_categoria=F('subtipo_movimiento__categoria_movimiento_id'),
                nombre=F('subtipo_movimiento__categoria_movimiento__nombre'))
    subtipos = objeto.distinct('subtipo_movimiento')\
        .values(id_subtipo=F('subtipo_movimiento_id'),
                id_categoria=F('subtipo_movimiento__categoria_movimiento_id'),
                nombre=F('subtipo_movimiento__nombre'))
    procesos = objeto.filter(flujo_caja_enc__contrato__isnull=True).distinct('flujo_caja_enc__proceso')\
        .values(contrato=F('flujo_caja_enc__contrato__numero_contrato'),
                proceso=F('flujo_caja_enc__proceso__nombre'),
                id_flujo_caja=F('flujo_caja_enc_id'),
                id_subtipo=F('subtipo_movimiento__id'))
    contratos = objeto.filter(flujo_caja_enc__proceso__isnull=True).distinct('flujo_caja_enc__contrato') \
        .values(contrato=F('flujo_caja_enc__contrato__numero_contrato'),
                proceso=F('flujo_caja_enc__proceso__nombre'),
                id_flujo_caja=F('flujo_caja_enc_id'),
                id_subtipo=F('subtipo_movimiento__id'))

    lista_procesos_contratos = []

    for pro in procesos:
        lista_procesos_contratos.append(pro)

    for con in contratos:
        lista_procesos_contratos.append(con)
    lista_meses = []
    pos_mes = 1
    lista_categorias = []
    total_ingresos_real = 0
    total_ingresos_proyectado = 0
    total_costos_real = 0
    total_costos_proyectado = 0
    total_gastos_real = 0
    total_gastos_proyectado = 0

    for cat in categorias:
        lista_subtipos = []
        for sub in subtipos:
            valor_con_pro = 0
            if sub['id_categoria'] == cat['id_categoria']:

                lista_con_pro = []

                # Inicio del for de contratos
                for con_pro in lista_procesos_contratos:
                    fecha_minima_con_pro = fecha_minima
                    valores_mes_con_pro = []

                    while obtener_fecha_inicio_de_mes(fecha_maxima.year, fecha_maxima.month) >= \
                            obtener_fecha_inicio_de_mes(fecha_minima_con_pro.year, fecha_minima_con_pro.month):
                        valor_con_pro_ingresos_real = 0
                        valor_con_pro_ingresos_proyectado = 0
                        valor_con_pro_costos_real = 0
                        valor_con_pro_costos_proyectado = 0
                        valor_con_pro_gastos_real = 0
                        valor_con_pro_gastos_proyectado = 0

                        inicio_mes = obtener_fecha_inicio_de_mes(fecha_minima_con_pro.year, fecha_minima_con_pro.month)
                        fin_mes = obtener_fecha_fin_de_mes(fecha_minima_con_pro.year, fecha_minima_con_pro.month)
                        objeto_con_pro = objeto.filter(fecha_movimiento__range=[inicio_mes, fin_mes],
                                                       flujo_caja_enc=con_pro['id_flujo_caja'],
                                                       subtipo_movimiento_id=sub['id_subtipo'])
                        for ocp in objeto_con_pro:
                            if ocp.tipo_registro == REAL:
                                if ocp.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                                    valor_con_pro_ingresos_real += ocp.valor
                                elif ocp.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.COSTOS:
                                    valor_con_pro_costos_real += ocp.valor
                                elif ocp.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.GASTOS:
                                    valor_con_pro_gastos_real += ocp.valor
                            else:
                                if ocp.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                                    valor_con_pro_ingresos_proyectado += ocp.valor
                                elif ocp.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.COSTOS:
                                    valor_con_pro_costos_proyectado += ocp.valor
                                elif ocp.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.GASTOS:
                                    valor_con_pro_gastos_proyectado += ocp.valor

                            valor_con_pro += ocp.valor

                        valores_mes_con_pro.append({
                            'mes': mes_numero_a_letras(fecha_minima_con_pro.month),
                            'valor_ingresos_real': valor_con_pro_ingresos_real,
                            'valor_ingresos_proyectado': valor_con_pro_ingresos_proyectado,
                            'valor_costos_real': valor_con_pro_costos_real,
                            'valor_costos_proyectado': valor_con_pro_costos_proyectado,
                            'valor_gastos_real': valor_con_pro_gastos_real,
                            'valor_gastos_proyectado': valor_con_pro_gastos_proyectado})

                        fecha_minima_con_pro = sumar_meses(fecha_minima_con_pro, 1)

                    if con_pro['contrato']:
                        nombre = con_pro['contrato']
                    else:
                        nombre = con_pro['proceso']
                    if valor_con_pro > 0:
                        lista_con_pro.append({'nombre': nombre, 'meses': valores_mes_con_pro})
                # Fin del for de contratos

                fecha_minima_subtipos = fecha_minima
                valores_mes_subtipos = []
                while obtener_fecha_inicio_de_mes(fecha_maxima.year, fecha_maxima.month) >= \
                        obtener_fecha_inicio_de_mes(fecha_minima_subtipos.year, fecha_minima_subtipos.month):
                    valor_subtipos_ingresos_real = 0
                    valor_subtipos_ingresos_proyectado = 0
                    valor_subtipos_costos_real = 0
                    valor_subtipos_costos_proyectado = 0
                    valor_subtipos_gastos_real = 0
                    valor_subtipos_gastos_proyectado = 0

                    inicio_mes = obtener_fecha_inicio_de_mes(fecha_minima_subtipos.year, fecha_minima_subtipos.month)
                    fin_mes = obtener_fecha_fin_de_mes(fecha_minima_subtipos.year, fecha_minima_subtipos.month)
                    objeto_subtipos = objeto.filter(fecha_movimiento__range=[inicio_mes, fin_mes],
                                                    subtipo_movimiento_id=sub['id_subtipo'])

                    for os in objeto_subtipos:
                        if os.tipo_registro == REAL:
                            if os.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                                valor_subtipos_ingresos_real += os.valor
                            elif os.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.COSTOS:
                                valor_subtipos_costos_real += os.valor
                            elif os.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.GASTOS:
                                valor_subtipos_gastos_real += os.valor
                        else:
                            if os.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                                valor_subtipos_ingresos_proyectado += os.valor
                            elif os.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.COSTOS:
                                valor_subtipos_costos_proyectado += os.valor
                            elif os.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.GASTOS:
                                valor_subtipos_gastos_proyectado += os.valor

                    valores_mes_subtipos.append(
                        {'mes': mes_numero_a_letras(fecha_minima_subtipos.month),
                         'valor_ingresos_real': valor_subtipos_ingresos_real,
                         'valor_ingresos_proyectado': valor_subtipos_ingresos_proyectado,
                         'valor_costos_real': valor_subtipos_costos_real,
                         'valor_costos_proyectado': valor_subtipos_costos_proyectado,
                         'valor_gastos_real': valor_subtipos_gastos_real,
                         'valor_gastos_proyectado': valor_subtipos_gastos_proyectado})
                    fecha_minima_subtipos = sumar_meses(fecha_minima_subtipos, 1)

                lista_subtipos.append({'id': sub['id_subtipo'], 'nombre': sub['nombre'], 'con_pro': lista_con_pro,
                                       'meses': valores_mes_subtipos})

        fecha_minima_categorias = fecha_minima
        valores_mes_categorias = []
        while obtener_fecha_inicio_de_mes(fecha_maxima.year, fecha_maxima.month) >= \
                obtener_fecha_inicio_de_mes(fecha_minima_categorias.year, fecha_minima_categorias.month):
            valor_cat_ingresos_real = 0
            valor_cat_ingresos_proyectado = 0
            valor_cat_costos_real = 0
            valor_cat_costos_proyectado = 0
            valor_cat_gastos_real = 0
            valor_cat_gastos_proyectado = 0

            inicio_mes = obtener_fecha_inicio_de_mes(fecha_minima_categorias.year, fecha_minima_categorias.month)
            fin_mes = obtener_fecha_fin_de_mes(fecha_minima_categorias.year, fecha_minima_categorias.month)
            objeto_categorias = objeto.filter(fecha_movimiento__range=[inicio_mes, fin_mes],
                                              subtipo_movimiento__categoria_movimiento_id=cat['id_categoria'])
            for oc in objeto_categorias:
                if oc.tipo_registro == REAL:
                    if oc.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                        valor_cat_ingresos_real += oc.valor
                    elif oc.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.COSTOS:
                        valor_cat_costos_real += oc.valor
                    elif oc.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.GASTOS:
                        valor_cat_gastos_real += oc.valor
                else:
                    if oc.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                        valor_cat_ingresos_proyectado += oc.valor
                    elif oc.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.COSTOS:
                        valor_cat_costos_proyectado += oc.valor
                    elif oc.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.GASTOS:
                        valor_cat_gastos_proyectado += oc.valor
            valores_mes_categorias.append(
                {'mes': mes_numero_a_letras(fecha_minima_categorias.month),
                 'valor_ingresos_real': valor_cat_ingresos_real,
                 'valor_ingresos_proyectado': valor_cat_ingresos_proyectado,
                 'valor_costos_real': valor_cat_costos_real,
                 'valor_costos_proyectado': valor_cat_costos_proyectado,
                 'valor_gastos_real': valor_cat_gastos_real,
                 'valor_gastos_proyectado': valor_cat_gastos_proyectado})

            coincidencia = False
            for mes in lista_meses:
                if mes['numero'] == fecha_minima_categorias.month and mes['anho'] == fecha_minima_categorias.year:
                    coincidencia = True
            if not coincidencia:
                lista_meses.append({'numero': fecha_minima_categorias.month, 'pos': pos_mes,
                                    'mes': mes_numero_a_letras(fecha_minima_categorias.month),
                                    'anho': fecha_minima_categorias.year})
                pos_mes += 1

            fecha_minima_categorias = sumar_meses(fecha_minima_categorias, 1)

            total_ingresos_real += valor_cat_ingresos_real
            total_ingresos_proyectado += valor_cat_ingresos_proyectado
            total_costos_real += valor_cat_costos_real
            total_costos_proyectado += valor_cat_costos_proyectado
            total_gastos_real += valor_cat_gastos_real
            total_gastos_proyectado += valor_cat_gastos_proyectado

        lista_categorias.append({'id': cat['id_categoria'], 'nombre': cat['nombre'], 'subtipos': lista_subtipos,
                                 'meses': valores_mes_categorias})

    totales = {'total_ingresos_real': total_ingresos_real,
               'total_ingresos_proyectado': total_ingresos_proyectado,
               'total_costos_real': total_costos_real,
               'total_costos_proyectado': total_costos_proyectado,
               'total_gastos_real': total_gastos_real,
               'total_gastos_proyectado': total_gastos_proyectado,
               'diferencia_ingresos_egresos_real': total_ingresos_real - total_costos_real - total_gastos_real,
               'diferencia_ingresos_egresos_proyectado':
                   total_ingresos_proyectado - total_costos_proyectado - total_gastos_proyectado,
               }

    return {'lista_categorias': lista_categorias, 'totales': totales, 'lista_meses': lista_meses}

