from datetime import datetime

from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse

from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import SubTipoMovimiento, TipoMovimiento
from Financiero.models.flujo_caja import CategoriaMovimiento


class SubtiposMovimientosView(AbstractEvaLoggedView):
    def get(self, request):
        subtip_movimientos = SubTipoMovimiento.objects.all()
        return render(request, 'Financiero/FlujoCaja/SubtipoMovimiento/index.html',
                      {'subtip_movimientos': subtip_movimientos, 'fecha': datetime.now(),
                       'menu_actual': ['flujo_caja', 'subtipos_movimientos']})


class SubtipoMovimientoCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Financiero/FlujoCaja/SubtipoMovimiento/modal-crear-editar.html',
                      datos_xa_render(self.OPCION))

    def post(self, request):
        subtipo_movimiento = SubTipoMovimiento.from_dictionary(request.POST)
        interpretar_radio_solo_contrato_proceso(subtipo_movimiento, request.POST.get('solo_contrato_proceso', ''))
        subtipo_movimiento.save()
        messages.success(request, 'Se ha creado el subtipo de movimiento {0}'.format(subtipo_movimiento.nombre))
        return redirect(reverse('financiero:subtipo-movimiento-index'))


class SubtipoMovimientoEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        sub_mov = SubTipoMovimiento.objects.get(id=id)
        return render(request, 'Financiero/FlujoCaja/SubtipoMovimiento/modal-crear-editar.html',
                      datos_xa_render(self.OPCION, sub_mov))

    def post(self, request, id):
        update_fields = ['nombre', 'descripcion', 'tipo_movimiento', 'categoria_movimiento', 'protegido', 'estado',
                         'solo_proceso', 'solo_contrato']
        sub_mov = SubTipoMovimiento.from_dictionary(request.POST)
        sub_mov = interpretar_radio_solo_contrato_proceso(sub_mov, request.POST.get('solo_contrato_proceso', ''))
        sub_mov.id = id
        sub_mov.estado = request.POST.get('estado', 'False') == 'True'
        sub_mov.save(update_fields=update_fields)
        messages.success(request, 'Se ha editado el subtipo de movimiento {0}'.format(sub_mov.nombre))
        return redirect(reverse('Financiero:subtipo-movimiento-index'))


def interpretar_radio_solo_contrato_proceso(subtipo_movimiento, valor):
    subtipo_movimiento.solo_contrato = False
    subtipo_movimiento.solo_proceso = False
    if valor == '1':
        subtipo_movimiento.solo_contrato = True
        subtipo_movimiento.solo_proceso = False
    elif valor == '2':
        subtipo_movimiento.solo_contrato = False
        subtipo_movimiento.solo_proceso = True
    return subtipo_movimiento


class SubtipoMovimientoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            sub_mov = SubTipoMovimiento.objects.get(id=id)
            sub_mov.delete()
            messages.success(request, 'Se ha eliminado el subtipo de movimiento {0}'.format(sub_mov.nombre))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error", "mensaje": "Este subtipo de movimiento no puede ser eliminado "
                                                               "porque ya se encuentra en uso."})


# region Métodos de ayuda
def datos_xa_render(opcion: str, sub_mov: SubTipoMovimiento = None) -> dict:
    """
    Datos necesarios para la creación de los html de los Subtipos de Movimientos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param sub_mov: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """
    tipos_movimientos = TipoMovimiento.objects.get_xa_select_activos()
    categorias_movimientos = CategoriaMovimiento.objects.get_xa_select_activos()
    opciones_solo_contrato_proceso = [{'valor': 0, 'texto': 'Ambos'},
                                      {'valor': 1, 'texto': 'Contratos'},
                                      {'valor': 2, 'texto': 'Procesos'}]
    datos = {'opcion': opcion, 'tipos_movimientos': tipos_movimientos,
             'opciones_solo_contrato_proceso': opciones_solo_contrato_proceso,
             'menu_actual': 'subtip_movimientos', 'categorias_movimientos': categorias_movimientos}
    if sub_mov:
        datos['sub_mov'] = sub_mov
        valor = 0
        if sub_mov.solo_contrato:
            valor = 1
        elif sub_mov.solo_proceso:
            valor = 2
        datos['solo_contrato_proceso'] = valor

    return datos
# endregion
