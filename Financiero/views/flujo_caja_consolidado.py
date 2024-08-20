import copy
import json
import os

import xlsxwriter

from datetime import datetime
from random import randrange

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, DateField, F
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from xlsxwriter.worksheet import Worksheet

from Administracion.models import Empresa, Proceso
from Administracion.utils import get_id_empresa_global
from EVA import settings
from EVA.General import app_date_now, app_datetime_now
from EVA.General.conversiones import add_months, mes_numero_a_letras, fijar_fecha_inicio_mes, datetime_to_filename
from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaEncabezado
from Financiero.models.flujo_caja import SubTipoMovimiento, FlujoCajaDetalle, EstadoFCDetalle, CategoriaMovimiento, \
    TipoMovimiento
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorProceso

COMPARATIVO = 2
PROYECTADO = 1
REAL = 0


class FlujoCajaConsolidadoView(AbstractEvaLoggedView):
    def get(self, request):
        if not request.user.has_perm('TalentoHumano.can_access_usuarioespecial')\
                and not request.user.has_perm('Financiero.view_flujocajadetalle'):
            return redirect(reverse('eva-index'))

        return render(request, 'Financiero/FlujoCaja/FlujoCajaConsolidado/index.html',
                      datos_xa_render(
                          request,
                          es_usuario_especial=request.user.has_perms('TalentoHumano.can_access_usuarioespecial'),
                          procesos_usuario=ColaboradorProceso.objects.get_ids_procesos_list(usuario=request.user)
                      ))

    def post(self, request):
        if not request.user.has_perm('TalentoHumano.can_access_usuarioespecial') \
                and not request.user.has_perm('Financiero.view_flujocajadetalle'):
            return redirect(reverse('eva-index'))

        es_usuario_especial = request.user.has_perms('TalentoHumano.can_access_usuarioespecial')
        procesos_usuario = ColaboradorProceso.objects.get_ids_procesos_list(usuario=request.user)

        datos = datos_formulario_consolidado(request)
        fecha_desde = datos['fecha_desde'] if datos['fecha_desde'] else datos['fecha_min']
        fecha_hasta = datos['fecha_hasta'] if datos['fecha_hasta'] else datos['fecha_max']

        tipos_flujos_caja = [datos['tipos_flujos_caja']] if '' != datos['tipos_flujos_caja'] != 2 else [0, 1]

        estados = datos['estados'] if datos['estados'] else [1, 2, 4, 5]

        if datos['subtipos']:
            subtipos = datos['subtipos']
        else:
            subtipos = SubTipoMovimiento.objects.all()
            if not es_usuario_especial:
                subtipos = subtipos.exclude(protegido=True)
            subtipos = list(subtipos.values_list('id', flat=True))

        categorias = datos['categorias'] if datos['categorias'] else list(CategoriaMovimiento.objects.all()
                                                                          .values_list('id', flat=True))

        con_pro = []

        if datos['lista_contratos']:
            con_pro.extend(list(FlujoCajaEncabezado.objects
                                .filter(contrato_id__in=datos['lista_contratos'])
                                .values_list('id', flat=True)))
        elif not datos['lista_procesos'] or not datos['lista_empresas']:
            if es_usuario_especial:
                con_pro.extend(FlujoCajaEncabezado.objects.get_id_flujos_contratos())
            else:
                con_pro.extend(list(FlujoCajaEncabezado.objects
                                    .filter(contrato__proceso_a_cargo_id__in=procesos_usuario)
                                    .values_list('id', flat=True)))

        if datos['lista_procesos']:
            con_pro.extend(list(FlujoCajaEncabezado.objects
                                .filter(proceso_id__in=datos['lista_procesos'])
                                .values_list('id', flat=True)))

        elif not datos['lista_contratos'] or not datos['lista_empresas']:
            if es_usuario_especial:
                con_pro.extend(FlujoCajaEncabezado.objects.get_id_flujos_procesos())
            else:
                con_pro.extend(list(FlujoCajaEncabezado.objects
                                    .filter(proceso_id__in=procesos_usuario)
                                    .values_list('id', flat=True)))
        empresas = []
        if datos['lista_empresas']:
            empresas.extend(datos['lista_empresas'])
        elif not datos['lista_empresas']:
            empresas.extend(list(Empresa.objects.all().values_list('id', flat=True)))
        movimientos = FlujoCajaDetalle.objects\
            .filter(estado_id__in=estados, flujo_caja_enc__in=con_pro,
                    fecha_movimiento__range=[fecha_desde, fecha_hasta], tipo_registro__in=tipos_flujos_caja,
                    subtipo_movimiento_id__in=subtipos,
                    subtipo_movimiento__categoria_movimiento__in=categorias,
                    flujo_caja_enc__empresa_id__in=empresas)\
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)
        if not movimientos:
            messages.warning(request, 'No se encontraron concidencias')

        datos_filtro = {'estados': estados, 'ids_flujos': con_pro, 'fecha_desde': fecha_desde,
                        'fecha_hasta': fecha_hasta, 'tipos_registro': tipos_flujos_caja, 'subtipos': subtipos,
                        'categorias': categorias, 'empresas': empresas}

        datos_render = datos_xa_render(request, datos, movimientos, datos_filtro, es_usuario_especial, procesos_usuario)

        if request.path.endswith('descargar'):
            nombre_excel = f'FC_{"Proyectado" if datos["tipos_flujos_caja"] == PROYECTADO else "Real"}' \
                           f'_{request.user.id}_{randrange(1,1000)}.xlsx'

            nombre_excel = os.path.join(settings.EVA_RUTA_ARCHIVOS_TEMPORALES, nombre_excel)

            self.generar_excel(nombre_excel, datos_render, datos['tipos_flujos_caja'])

            return FileResponse(open(nombre_excel, 'rb'),
                                filename=f"Flujo de Caja {datetime_to_filename(app_datetime_now())}.xlsx")
        else:
            return render(request, 'Financiero/FlujoCaja/FlujoCajaConsolidado/index.html', datos_render)

    def generar_excel(self, nombre, datos: dict, tipo_consolidado):

        # Constantes de los niveles para la agrupación de filas.
        NIVEL_TIPO = 0
        NIVEL_CATEGORIA = 1
        NIVEL_SUBTIPO = 2

        workbook = xlsxwriter.Workbook(nombre)

        # Formatos para las celdas.
        bold = workbook.add_format({'bold': True, 'border': 2})
        bold_center = workbook.add_format({'bold': True, 'align': 'center'})
        money = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        money_bold = workbook.add_format({'num_format': '#,##0.00', 'bold': True, 'border': 2})
        borde_1 = workbook.add_format({'border': 1})

        worksheet = workbook.add_worksheet('Flujo de Caja')

        # Título de la hoja.
        worksheet.merge_range(0, 0, 0, 5, "Flujo de Caja", bold_center)

        fila = 2
        col = 1

        # Se fija el ancho de las columnas.
        worksheet.set_column(0, 0, 40, None, None)
        worksheet.set_column(1, len(datos['meses']), 16, None, None)

        # Se agrega la filas con los meses.
        for mes in datos['meses']:
            worksheet.write(fila, col, f"{mes['mes']} {mes['anho']}", borde_1)
            col += 1

        fila += 1

        nombre_campo_totales = 'valor_proyectado' if tipo_consolidado == PROYECTADO else 'valor_real'

        # Se agregan las filas con los movimientos agregando sub totales para las categorías y tipos de movimientos.
        for tipo in datos['movimientos']:
            if tipo_consolidado == PROYECTADO:
                nombre_campo = 'valor_costos_proyectado' if tipo['id_tipo'] == 1 else 'valor_gastos_proyectado' \
                    if tipo['id_tipo'] == 2 else 'valor_ingresos_proyectado'
            else:
                nombre_campo = 'valor_costos_real' if tipo['id_tipo'] == 1 else 'valor_gastos_real' \
                    if tipo['id_tipo'] == 2 else 'valor_ingresos_real'

            for categoria in tipo['valores']:
                for subtipo in categoria['subtipos']:
                    self.agregar_fila_excel(worksheet, fila, subtipo['meses'], (subtipo['nombre'], borde_1),
                                            (nombre_campo, money),
                                            {'level': NIVEL_SUBTIPO, 'hidden': True})
                    fila += 1

                self.agregar_fila_excel(worksheet, fila, categoria['meses'], (categoria['nombre'], bold),
                                        (nombre_campo, money_bold),
                                        {'level': NIVEL_CATEGORIA, 'collapsed': True, 'hidden': True})
                fila += 1

            self.agregar_fila_excel(worksheet, fila, tipo['meses'], (tipo['nombre_tipo'].upper(), bold),
                              (nombre_campo_totales, money_bold),
                              {'level': NIVEL_TIPO, 'collapsed': True})
            fila += 1

        self.agregar_fila_excel(worksheet, fila, datos['totales_mes_a_mes'], ('Total', bold),
                          (nombre_campo_totales, money_bold), None)
        workbook.close()

    @staticmethod
    def agregar_fila_excel(worksheet: Worksheet, fila, datos_meses, nombre_fila, nombre_campo, opciones):
        worksheet.set_row(fila, None, None, opciones)
        worksheet.write(fila, 0, nombre_fila[0], nombre_fila[1])
        col = 1
        for info_mes in datos_meses:
            worksheet.write(fila, col, info_mes[nombre_campo[0]], nombre_campo[1])
            col += 1


def datos_xa_render(request, datos_formulario=None, movimientos=None, datos_filtro: {} = None,
                    es_usuario_especial=False, procesos_usuario: [] = None):
    fecha_min, fecha_max = obtener_fechas_min_max_fc('')

    fecha_min_max = json.dumps({'fecha_min': str(fecha_min),
                                'fecha_max': str(fecha_max)})

    empresas = Empresa.objects.get_xa_select()
    procesos = Proceso.objects.get_xa_select()
    contratos = Contrato.objects.get_xa_select_x_empresa(get_id_empresa_global(request))
    subtipos = SubTipoMovimiento.objects.get_xa_select_activos()

    procesos_usuario = ColaboradorProceso.objects.get_ids_procesos_list(usuario=request.user)

    if not es_usuario_especial:
        subtipos = subtipos.exclude(protegido=True)
        procesos = procesos.filter(id__in=procesos_usuario)
        contratos = contratos.filter(proceso_a_cargo_id__in=procesos_usuario)

    categorias = CategoriaMovimiento.objects.get_xa_select_activos()
    subtipos_categorias = []
    for sub in SubTipoMovimiento.objects.all():
        subtipos_categorias.append({'id': sub.id, 'nombre': sub.nombre, 'categoria_id': sub.categoria_movimiento_id})

    tipos_flujos = [{'campo_valor': 1, 'campo_texto': 'Proyectado'},
                    {'campo_valor': 2, 'campo_texto': 'Comparativo'}]

    estados = [{'campo_valor': 1, 'campo_texto': 'Vigente'},
               {'campo_valor': 2, 'campo_texto': 'Editado'},
               {'campo_valor': 4, 'campo_texto': 'Eliminado'},
               {'campo_valor': 5, 'campo_texto': 'Aplicado'}]

    datos = {'procesos': procesos, 'contratos': contratos, 'tipos_flujos': tipos_flujos, 'estados': estados,
             'categorias': categorias, 'subtipos': subtipos, 'fecha_actual': datetime.today(), 'empresas': empresas,
             'subtipos_categorias': json.dumps(subtipos_categorias), 'fecha_min_max': fecha_min_max,
             'menu_actual': ['flujo_caja', 'consolidado']}

    quitar_selecciones = {'texto': 'Quitar Selecciones', 'icono': 'fa-times'}
    seleccionar_todos = {'texto': 'Seleccionar Todos', 'icono': 'fa-check'}
    datos['textos_empresas'] = seleccionar_todos
    datos['textos_contratos'] = seleccionar_todos
    datos['textos_procesos'] = seleccionar_todos
    datos['textos_subtipos'] = seleccionar_todos
    datos['textos_categorias'] = seleccionar_todos

    if datos_formulario:
        datos['valor'] = datos_formulario

        if datos_formulario['lista_empresas']:
            datos['textos_empresas'] = quitar_selecciones

        if datos_formulario['lista_contratos']:
            datos['textos_contratos'] = quitar_selecciones

        if datos_formulario['lista_procesos']:
            datos['textos_procesos'] = quitar_selecciones
            datos['contratos'] = Contrato.objects.filter(proceso_a_cargo__in=datos_formulario['lista_procesos'],
                                                         empresa_id__in=datos_formulario['lista_empresas']) \
                .values(campo_valor=F('id'), campo_texto=F('numero_contrato'))
        if datos_formulario['subtipos']:
            datos['textos_subtipos'] = quitar_selecciones

        if datos_formulario['categorias']:
            datos['textos_categorias'] = quitar_selecciones

        if datos_formulario['tipos_flujos_caja'] == COMPARATIVO:
            datos['comparativo'] = True

    else:
        datos['valor'] = {'estados': [1, 2, 5], 'lista_empresas': [get_id_empresa_global(request)]}

    if movimientos:
        consolidado = consolidado_ingresos_costos_gastos(movimientos, datos_filtro)
        datos['movimientos'] = consolidado['consolidado']
        datos['totales'] = consolidado['totales']
        datos['meses'] = consolidado['lista_meses']

        # Se deja inicialmente como se estaba calculando, pero se dbe evaluar la posibilidad de hacer un refactor
        # y hacer los cálculos en la función que realiza el consolidado.
        total_mes_a_mes = []
        for mes in datos['meses']:
            suma_mes_real = 0
            suma_mes_proyectado = 0

            total_ingresos = sumar_consolidado_mes_a_mes(consolidado, mes, TipoMovimiento.COSTOS)
            suma_mes_real -= total_ingresos['suma_mes_real']
            suma_mes_proyectado -= total_ingresos['suma_mes_proyectado']

            total_ingresos = sumar_consolidado_mes_a_mes(consolidado, mes, TipoMovimiento.GASTOS)
            suma_mes_real -= total_ingresos['suma_mes_real']
            suma_mes_proyectado -= total_ingresos['suma_mes_proyectado']

            total_ingresos = sumar_consolidado_mes_a_mes(consolidado, mes, TipoMovimiento.INGRESOS)
            suma_mes_real += total_ingresos['suma_mes_real']
            suma_mes_proyectado += total_ingresos['suma_mes_proyectado']

            total_mes_a_mes.append({'mes': mes['mes'], 'valor_real': suma_mes_real,
                                    'valor_proyectado': suma_mes_proyectado})

        datos['totales_mes_a_mes'] = total_mes_a_mes

    return datos


def sumar_consolidado_mes_a_mes(consolidado, mes, tipo):
    suma_mes_real = 0
    suma_mes_proyectado = 0
    for tipos in consolidado['consolidado']:
        for m in tipos['meses']:
            if m['mes'] == mes['mes'] and m['anho'] == mes['anho'] and \
                    tipos['id_tipo'] == tipo:
                suma_mes_real += m['valor_real']
                suma_mes_proyectado += m['valor_proyectado']
    return {'suma_mes_real': suma_mes_real, 'suma_mes_proyectado': suma_mes_proyectado}


def datos_formulario_consolidado(request):
    empresas = request.POST.getlist('empresa[]', [])
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

    empresas = list(map(int, empresas))
    procesos = list(map(int, procesos))
    contratos = list(map(int, contratos))
    estados = list(map(int, estados)) if estados else [1, 2, 5]
    subtipos = list(map(int, subtipos))
    categorias = list(map(int, categorias))

    if tipos_flujos_caja:
        tipos_flujos_caja = int(tipos_flujos_caja)

    fecha_min, fecha_max = obtener_fechas_min_max_fc(app_datetime_now())

    return {'lista_procesos': procesos, 'lista_contratos': contratos, 'lista_empresas': empresas,
            'fecha_hasta': fecha_hasta, 'subtipos': subtipos, 'tipos_flujos_caja': tipos_flujos_caja,
            'estados': estados, 'fecha_min': fecha_min, 'fecha_max': fecha_max, 'categorias': categorias,
            'fecha_desde': fecha_desde}


def obtener_fecha_minima(objeto):
    if objeto:
        primera_fecha = objeto.order_by('fecha_movimiento').first().fecha_movimiento.date()
    else:
        primera_fecha = app_date_now()
    return fijar_fecha_inicio_mes(primera_fecha)


def obtener_fecha_maxima(objeto):
    if objeto:
        ultima_fecha = objeto.order_by('fecha_movimiento').last().fecha_movimiento.date()
    else:
        ultima_fecha = app_date_now()
    return fijar_fecha_inicio_mes(ultima_fecha)


def consolidado_ingresos_costos_gastos(movimientos, datos_filtro):
    """
    Genera el consolidado de flujos de caja según los filtros especificados.
    :param movimientos: Movimientos a los que les aplica el filtro. (Se debe evaluar si aplica dejarlo, solo se esta
    usando para determinar la fecha mínima y máxima).
    :param datos_filtro: datos_filtro: Diccionario con todos los datos de los filtros a aplicar en las consultas.
    :return: Retorna un diccionario con el resultado del consolidado agrupado por tipo -> categoría -> subtipo ->
    proceso/contrato, los totales y listado de los meses para el cual aplica el consolidado.
    """
    fecha_minima = obtener_fecha_minima(movimientos)
    fecha_maxima = obtener_fecha_maxima(movimientos)
    meses = crear_lista_meses(fecha_minima, fecha_maxima)
    meses_catsub = obtener_meses_xa_catsub(meses)
    tipos_mov = TipoMovimiento.objects.all()
    categorias = CategoriaMovimiento.objects.filter(id__in=datos_filtro['categorias'])
    consol = []
    totales = []

    for tipo_mov in tipos_mov:
        consol.append({'id_tipo': tipo_mov.id, 'nombre_tipo': tipo_mov.nombre, 'meses': obtener_meses_xa_tipo(meses),
                       'valores': []})
        totales.append({'total_real': 0, 'total_proyectado': 0})
        for categoria in categorias:
            valores_cat = {'id': categoria.id, 'nombre': categoria.nombre, 'meses': copy.deepcopy(meses_catsub),
                           'subtipos': []}

            if consolidado_llenar_categoria(valores_cat, tipo_mov, datos_filtro, meses_catsub):
                consol[-1]['valores'].append(valores_cat)
                for i, mes in enumerate(valores_cat['meses']):
                    add_valor_mes_tipo(mes, consol[-1]['meses'], i, totales[-1])

    totales = {'total_ingresos_real': totales[2]['total_real'],
               'total_ingresos_proyectado': totales[2]['total_proyectado'],
               'total_costos_real': totales[0]['total_real'],
               'total_costos_proyectado': totales[0]['total_proyectado'],
               'total_gastos_real': totales[1]['total_real'],
               'total_gastos_proyectado': totales[1]['total_proyectado'],
               'diferencia_ingresos_egresos_real': (totales[2]['total_real'] -
                                                    totales[1]['total_real'] -
                                                    totales[0]['total_real']),
               'diferencia_ingresos_egresos_proyectado': (totales[2]['total_proyectado'] -
                                                          totales[1]['total_proyectado'] -
                                                          totales[0]['total_proyectado'])
               }

    return {'consolidado': consol, 'totales': totales, 'lista_meses': obtener_meses_xa_tipo(meses)}


def consolidado_llenar_categoria(valores_cat: {}, tipo_mov, datos_filtro, meses):
    """
    Crea toda la estructura de datos con los valores correspondientes a todos los movimientos relacionados para una
    categoría especifica.  Los datos se agrupan por subtipo de movimiento y en cada uno de estos por contrato o proceso.
    :param valores_cat: Diccionario con la información de la categoría.
    :param tipo_mov: Tipo del movimiento al que aplica Ingreso, Costo, Gasto.
    :param datos_filtro: Diccionario con todos los datos de los filtros a aplicar en las consultas.
    :param meses: Listado con los meses para que aplica el consolidado.
    :return: True si efectivamente se adicionaron datos de movimientos a la categoría correspondiente de lo contrario
    False.
    """
    subtipos = SubTipoMovimiento.objects.filter(id__in=datos_filtro['subtipos'],
                                                categoria_movimiento_id=valores_cat['id'],
                                                tipo_movimiento_id=tipo_mov.id)

    for subtipo in subtipos:
        valores_subtipo = {'id': subtipo.id, 'nombre': subtipo.nombre, 'meses':  copy.deepcopy(meses),
                           'con_pro': []}

        movimientos = FlujoCajaDetalle.objects\
            .filter(subtipo_movimiento_id=subtipo.id,
                    fecha_movimiento__range=[datos_filtro['fecha_desde'], datos_filtro['fecha_hasta']],
                    estado_id__in=datos_filtro['estados'],
                    tipo_registro__in=datos_filtro['tipos_registro'],
                    flujo_caja_enc_id__in=datos_filtro['ids_flujos'],
                    flujo_caja_enc__empresa_id__in=datos_filtro['empresas'])\
            .exclude(estado_id=EstadoFCDetalle.OBSOLETO)\
            .values('flujo_caja_enc__proceso__nombre', 'flujo_caja_enc__contrato__numero_contrato', 'tipo_registro',
                    fecha=TruncMonth('fecha_movimiento', output_field=DateField())).annotate(Sum('valor'))\
            .order_by('flujo_caja_enc__proceso__nombre', 'flujo_caja_enc__contrato__numero_contrato', 'fecha')

        nombre_conpro = ''
        for movimiento in movimientos:
            nombre = movimiento['flujo_caja_enc__proceso__nombre'] if movimiento['flujo_caja_enc__proceso__nombre'] else movimiento['flujo_caja_enc__contrato__numero_contrato']

            if nombre_conpro != nombre:
                nombre_conpro = nombre
                valores_mov = {'nombre': nombre, 'meses':  copy.deepcopy(meses)}
                valores_subtipo['con_pro'].append(valores_mov)

            add_valor_mes(movimiento['valor__sum'], movimiento['fecha'], movimiento['tipo_registro'], tipo_mov.id,
                          valores_subtipo['con_pro'][-1]['meses'])
            add_valor_mes(movimiento['valor__sum'], movimiento['fecha'], movimiento['tipo_registro'], tipo_mov.id,
                          valores_subtipo['meses'])
            add_valor_mes(movimiento['valor__sum'], movimiento['fecha'], movimiento['tipo_registro'], tipo_mov.id,
                          valores_cat['meses'])

        if nombre_conpro:
            valores_cat['subtipos'].append(valores_subtipo)

    return len(valores_cat['subtipos']) != 0


def add_valor_mes(valor, fecha, tipo_registro, tipo_mov, meses):
    """
    Adiciona el valor especificado a una lista de meses donde se tienen los acumuladores para los costos, gastos e
    ingreso tanto reales como proyectados, teniendo en cuenta la fecha, tipo de registro y tipo de movimiento
    especificado.
    :param valor: Valor a adicionar
    :param fecha: fecha para la que aplica el valor
    :param tipo_registro: Tipo que indica si se suma a Real o Proyectado
    :param tipo_mov: Tipo del movimiento al que aplica Ingreso, Costo, Gasto.
    :param meses: Lista de los meses que tienen los acumuladores y sobre la cual se hara la adición
    :return:
    """
    valor_real = 0
    valor_proyectado = 0
    for mes in meses:
        if mes['fecha'] == fecha:
            if tipo_registro == REAL:
                valor_real = valor
            else:
                valor_proyectado = valor

            if tipo_mov == TipoMovimiento.INGRESOS:
                mes['valor_ingresos_real'] += valor_real
                mes['valor_ingresos_proyectado'] += valor_proyectado
            elif tipo_mov == TipoMovimiento.COSTOS:
                mes['valor_costos_real'] += valor_real
                mes['valor_costos_proyectado'] += valor_proyectado
            elif tipo_mov == TipoMovimiento.GASTOS:
                mes['valor_gastos_real'] += valor_real
                mes['valor_gastos_proyectado'] += valor_proyectado


def add_valor_mes_tipo(mes, meses, pos_mes, totales):
    """
    Suma los valores correspondientes de un mes en el los totales de los meses
    :param mes: valores reales y proyectados para el mes de costos, gastos e ingresos.
    :param meses: Lista de meses en la cual se van adicionar los valores.
    :param pos_mes: posición del mes en la lista de meses al cual se le van adicionar los valores
    :param totales: diccionario donde se acumulan los totales para un tipo especifico de movimiento.
    :return: Nada
    """
    total_real = mes['valor_ingresos_real'] + mes['valor_costos_real'] + mes['valor_gastos_real']
    total_proyectado = mes['valor_ingresos_proyectado'] + mes['valor_costos_proyectado'] + mes['valor_gastos_proyectado']
    meses[pos_mes]['valor_real'] += total_real
    meses[pos_mes]['valor_proyectado'] += total_proyectado

    totales['total_real'] += total_real
    totales['total_proyectado'] += total_proyectado


def crear_lista_meses(fecha_minima, fecha_maxima):
    meses = []

    while fecha_minima <= fecha_maxima:
        meses.append({'fecha': fecha_minima, 'mes': mes_numero_a_letras(fecha_minima.month)})
        fecha_minima = add_months(fecha_minima, 1)
    return meses


def obtener_meses_xa_tipo(meses: []):
    meses_tipo = copy.deepcopy(meses)
    for mes in meses_tipo:
        mes.update({'anho':  mes['fecha'].year, 'valor_proyectado': 0, 'valor_real': 0})

    return meses_tipo


def obtener_meses_xa_catsub(meses: []):
    meses_catsub = copy.deepcopy(meses)
    for mes in meses_catsub:
        mes.update({'valor_ingresos_real': 0, 'valor_ingresos_proyectado': 0, 'valor_costos_real': 0,
                    'valor_costos_proyectado': 0, 'valor_gastos_real': 0, 'valor_gastos_proyectado': 0})

    return meses_catsub


def obtener_fechas_min_max_fc(valor_defecto):
    """
    Obtiene la fecha mínima y máxima de todos los movimientos de flujo de caja registrados.
    :param valor_defecto: Valor por defecto a retornar en caso de que no existan movimientos.
    :return: retorna la fecha mínima y máxima calculada en el orden que se mencionan.
    """
    movimientos = FlujoCajaDetalle.objects.all().order_by('fecha_movimiento')
    primer_movimiento = movimientos.first()
    if primer_movimiento:
        fecha_min = primer_movimiento.fecha_movimiento
        fecha_max = movimientos.last().fecha_movimiento
    else:
        fecha_min = valor_defecto
        fecha_max = valor_defecto
    return fecha_min, fecha_max


class ContratosXProcesos(AbstractEvaLoggedView):
    """
    Genera los datos necesarios para seleccionar los contratos relacionados a los procesos que recibe.
    :request: Recibe por GET la lista con los id de los procesos seleccionados en el formulario de consolidado,
    adicional a ello, realiza un filtro por empresa para distinguir los datos.
    :return: Retorna una lista con los id de los contratos.
    """
    def get(self, request):
        procesos = json.loads(request.GET.get('procesos', [])) if request.GET.get('procesos') else ''
        empresas = json.loads(request.GET.get('empresas', [])) if request.GET.get('empresas') else ''
        if procesos and empresas:
            contratos = Contrato.objects.filter(proceso_a_cargo_id__in=procesos, empresa_id__in=empresas)\
                .values(campo_valor=F('id'), campo_texto=F('numero_contrato'))
        elif procesos:
            contratos = Contrato.objects.filter(proceso_a_cargo_id__in=procesos) \
                .values(campo_valor=F('id'), campo_texto=F('numero_contrato'))
        elif empresas:
            contratos = Contrato.objects.filter(empresa_id__in=empresas) \
                .values(campo_valor=F('id'), campo_texto=F('numero_contrato'))
        else:
            contratos = Contrato.objects.get_xa_select_activos()
        contratos_json = json.dumps(list(contratos), cls=DjangoJSONEncoder)
        return JsonResponse({"estado": "OK", "datos": contratos_json})
