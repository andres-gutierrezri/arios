from datetime import datetime

from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse

from EVA.views.index import AbstractEvaLoggedView
from Financiero.models import SubTipoMovimiento, TipoMovimiento


class SubtiposMovimientosView(AbstractEvaLoggedView):
    def get(self, request):
        subtip_movimientos = SubTipoMovimiento.objects.all()
        return render(request, 'Financiero/FlujoCaja/SubtipoMovimiento/index.html',
                      {'subtip_movimientos': subtip_movimientos, 'fecha': datetime.now(),
                       'menu_actual': 'subtip_movimientos'})


class SubtipoMovimientoCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Financiero/FlujoCaja/SubtipoMovimiento/modal-crear-editar.html',
                      datos_xa_render(self.OPCION))

    def post(self, request):
        subtipo_movimiento = SubTipoMovimiento.from_dictionary(request.POST)
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
        update_fields = ['nombre', 'descripcion', 'tipo_movimiento', 'protegido', 'estado']
        sub_mov = SubTipoMovimiento.from_dictionary(request.POST)
        sub_mov.id = id
        sub_mov.estado = request.POST.get('estado', 'False') == 'True'
        sub_mov.save(update_fields=update_fields)
        messages.success(request, 'Se ha editado el subtipo de movimiento {0}'.format(sub_mov.nombre))
        return redirect(reverse('Financiero:subtipo-movimiento-index'))


class SubtipoMovimientoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            sub_mov = SubTipoMovimiento.objects.get(id=id)
            sub_mov.delete()
            messages.success(request, 'Se ha eliminado el subtipo de movimiento {0}'.format(sub_mov.nombre))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error", "mensaje": "Este subtipo de movimiento no puede ser eliminado"
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
    datos = {'opcion': opcion, 'tipos_movimientos': tipos_movimientos,
             'menu_actual': 'subtip_movimientos'}
    if sub_mov:
        datos['sub_mov'] = sub_mov

    return datos
# endregion
