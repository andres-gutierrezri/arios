import json
from datetime import datetime

from django.contrib import messages
from django.db.models import F
from django.shortcuts import render, redirect
from django.urls import reverse

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
    procesos_contratos = FlujoCajaDetalle.objects.all().order_by('fecha_crea')
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


def construir_consolidado(objeto):

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

    lista_categorias = []
    total_ingresos_real = 0
    total_ingresos_proyectado = 0
    total_egresos_real = 0
    total_egresos_proyectado = 0
    consolidado = {}

    for cat in categorias:
        valor_cat_ingresos_real = 0
        valor_cat_ingresos_proyectado = 0
        valor_cat_egresos_real = 0
        valor_cat_egresos_proyectado = 0

        lista_subtipos = []
        for sub in subtipos:
            valor_subtipos_ingresos_real = 0
            valor_subtipos_ingresos_proyectado = 0
            valor_subtipos_egresos_real = 0
            valor_subtipos_egresos_proyectado = 0

            if sub['id_categoria'] == cat['id_categoria']:

                lista_con_pro = []
                for con_pro in lista_procesos_contratos:
                    valor_con_pro = 0
                    valor_con_pro_ingresos_real = 0
                    valor_con_pro_ingresos_proyectado = 0
                    valor_con_pro_egresos_real = 0
                    valor_con_pro_egresos_proyectado = 0
                    for x in objeto.filter(flujo_caja_enc=con_pro['id_flujo_caja'],
                                           subtipo_movimiento_id=sub['id_subtipo']):
                        if x.tipo_registro == REAL:
                            if x.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                                valor_con_pro_ingresos_real += x.valor
                            else:
                                valor_con_pro_egresos_real += x.valor
                        else:
                            if x.subtipo_movimiento.tipo_movimiento_id == TipoMovimiento.INGRESOS:
                                valor_con_pro_ingresos_proyectado += x.valor
                            else:
                                valor_con_pro_egresos_proyectado += x.valor

                        valor_con_pro += x.valor

                    valor_subtipos_ingresos_real += valor_con_pro_ingresos_real
                    valor_subtipos_ingresos_proyectado += valor_con_pro_ingresos_proyectado
                    valor_subtipos_egresos_real += valor_con_pro_egresos_real
                    valor_subtipos_egresos_proyectado += valor_con_pro_egresos_proyectado

                    if con_pro['contrato']:
                        nombre = con_pro['contrato']
                    else:
                        nombre = con_pro['proceso']
                    if valor_con_pro > 0:
                        lista_con_pro.append({'nombre': nombre,
                                              'valor_ingresos_real': valor_con_pro_ingresos_real,
                                              'valor_ingresos_proyectado': valor_con_pro_ingresos_proyectado,
                                              'valor_egresos_real': valor_con_pro_egresos_real,
                                              'valor_egresos_proyectado': valor_con_pro_egresos_proyectado})

                valor_cat_ingresos_real += valor_subtipos_ingresos_real
                valor_cat_ingresos_proyectado += valor_subtipos_ingresos_proyectado
                valor_cat_egresos_real += valor_subtipos_egresos_real
                valor_cat_egresos_proyectado += valor_subtipos_egresos_proyectado

                lista_subtipos.append({'id': sub['id_subtipo'], 'nombre': sub['nombre'], 'con_pro': lista_con_pro,
                                       'valor_ingresos_real': valor_subtipos_ingresos_real,
                                       'valor_ingresos_proyectado': valor_subtipos_ingresos_proyectado,
                                       'valor_egresos_real': valor_subtipos_egresos_real,
                                       'valor_egresos_proyectado': valor_subtipos_egresos_proyectado})

        lista_categorias.append({'id': cat['id_categoria'], 'nombre': cat['nombre'], 'subtipos': lista_subtipos,
                                 'valor_ingresos_real': valor_cat_ingresos_real,
                                 'valor_ingresos_proyectado': valor_cat_ingresos_proyectado,
                                 'valor_egresos_real': valor_cat_egresos_real,
                                 'valor_egresos_proyectado': valor_cat_egresos_proyectado})

        total_ingresos_real += valor_cat_ingresos_real
        total_ingresos_proyectado += valor_cat_ingresos_proyectado
        total_egresos_real += valor_cat_egresos_real
        total_egresos_proyectado += valor_cat_egresos_proyectado

    consolidado['lista_categorias'] = lista_categorias
    consolidado['totales'] = {'total_ingresos_real': total_ingresos_real,
                              'total_ingresos_proyectado': total_ingresos_proyectado,
                              'total_egresos_real': total_egresos_real,
                              'total_egresos_proyectado': total_egresos_proyectado}

    return consolidado
