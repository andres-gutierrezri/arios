import json
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import FlujoCajaEncabezado
from Financiero.models.flujo_caja import SubTipoMovimiento, FlujoCajaDetalle, EstadoFCDetalle


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

        if datos['lista_procesos_contratos']:
            movimientos = FlujoCajaDetalle.objects\
                .filter(estado_id__in=estados, flujo_caja_enc__in=datos['lista_procesos_contratos'],
                        fecha_movimiento__range=[fecha_desde, fecha_hasta], tipo_registro__in=tipos_flujos_caja,
                        subtipo_movimiento_id__in=subtipos)\
                .exclude(estado_id=EstadoFCDetalle.OBSOLETO)
        else:
            movimientos = []

        comparacion = []
        if datos['tipos_flujos_caja'] == 2:
            real = movimientos.filter(tipo_registro=0)
            proyectado = movimientos.filter(tipo_registro=1)
            cant_real = real.count()
            cant_proyeccion = proyectado.count()

            if cant_real > cant_proyeccion:
                referencia = cant_real
            else:
                referencia = cant_proyeccion

            x = 0
            while x < referencia:
                if cant_real > x:
                    datos_real = real[x]
                else:
                    datos_real = ''

                if cant_proyeccion > x:
                    datos_proyectado = proyectado[x]
                else:
                    datos_proyectado = ''
                comparacion.append({'datos_real': datos_real,
                                    'datos_proyectado': datos_proyectado})
                x += 1

        if not movimientos or not comparacion:
            messages.warning(request, 'No se encontraron concidencias')
        return render(request, 'Financiero/FlujoCaja/FlujoCajaConsolidado/index.html',
                      datos_xa_render(datos, movimientos, comparacion))


def datos_xa_render(datos_formulario=None, movimientos=None, comparacion=None):
    procesos_contratos = FlujoCajaDetalle.objects.all().order_by('fecha_crea')
    if procesos_contratos:
        fecha_min = procesos_contratos.first().fecha_movimiento
        fecha_max = procesos_contratos.last().fecha_movimiento
    else:
        fecha_min = ''
        fecha_max = ''

    fecha_min_max = json.dumps({'fecha_min': str(fecha_min),
                                'fecha_max': str(fecha_max)})

    contratos_procesos = []
    for pro_con in FlujoCajaEncabezado.objects.all():
        if pro_con.contrato:
            contratos_procesos.append({'campo_valor': pro_con.id, 'campo_texto': pro_con.contrato})
        else:
            contratos_procesos.append({'campo_valor': pro_con.id, 'campo_texto': pro_con.proceso.nombre})

    subtipos = SubTipoMovimiento.objects.get_xa_select_activos()
    tipos_flujos = [{'campo_valor': 0, 'campo_texto': 'Real'},
                    {'campo_valor': 1, 'campo_texto': 'Proyectado'},
                    {'campo_valor': 2, 'campo_texto': 'Comparativo'}]

    estados = [{'campo_valor': 1, 'campo_texto': 'Vigente'},
               {'campo_valor': 2, 'campo_texto': 'Editado'},
               {'campo_valor': 4, 'campo_texto': 'Eliminado'}]

    datos = {'contratos_procesos': contratos_procesos, 'subtipos': subtipos, 'fecha_min_max': fecha_min_max,
             'tipos_flujos': tipos_flujos, 'estados': estados, 'fecha_actual': datetime.today()}

    quitar_selecciones = {'texto': 'Quitar Selecciones', 'icono': 'fa-times'}
    seleccionar_todos = {'texto': 'Seleccionar Todos', 'icono': 'fa-check'}
    datos['textos_pro_con'] = seleccionar_todos
    datos['textos_subtipos'] = seleccionar_todos

    if datos_formulario:
        datos['valor'] = datos_formulario

        if datos_formulario['lista_procesos_contratos']:
            datos['textos_pro_con'] = quitar_selecciones

        if datos_formulario['subtipos']:
            datos['textos_subtipos'] = quitar_selecciones

    else:
        datos['valor'] = {'estados': [1, 2]}

    if movimientos:
        datos['movimientos'] = movimientos

    if comparacion:
        datos['movimientos'] = ''
        datos['comparacion'] = comparacion

    return datos


def datos_formulario_consolidado(request):
    lista_procesos_contratos = request.POST.getlist('contrato_proceso[]', [])
    fecha_desde = request.POST.get('fecha_desde', '')
    fecha_hasta = request.POST.get('fecha_hasta', '')
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")

    subtipos = request.POST.getlist('subtipos[]', '')
    tipos_flujos_caja = request.POST.get('tipos_flujos_caja_id', '')
    estados = request.POST.getlist('estados[]', [])

    lista_con_pro = []
    for x in lista_procesos_contratos:
        lista_con_pro.append(int(x))

    if estados:
        lista_estados = []
        for y in estados:
            lista_estados.append(int(y))
    else:
        lista_estados = [1, 2]

    lista_subtipos = []
    for z in subtipos:
        lista_subtipos.append(int(z))

    if tipos_flujos_caja:
        tipos_flujos_caja = int(tipos_flujos_caja)

    movimientos = FlujoCajaDetalle.objects.all().order_by('fecha_crea')
    if movimientos:
        fecha_min = movimientos.first().fecha_movimiento
        fecha_max = movimientos.last().fecha_movimiento
    else:
        fecha_min = ''
        fecha_max = ''

    return {'lista_procesos_contratos': lista_con_pro, 'fecha_desde': fecha_desde, 'fecha_hasta': fecha_hasta,
            'subtipos': lista_subtipos, 'tipos_flujos_caja': tipos_flujos_caja, 'estados': lista_estados,
            'fecha_min': fecha_min, 'fecha_max': fecha_max}
