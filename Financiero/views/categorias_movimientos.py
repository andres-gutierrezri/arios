
from datetime import datetime

from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse

from EVA.views.index import AbstractEvaLoggedView
from Financiero.models.flujo_caja import CategoriaMovimiento


class CategoriasMovimientosView(AbstractEvaLoggedView):
    def get(self, request):
        categorias_movimientos = CategoriaMovimiento.objects.all()
        return render(request, 'Financiero/FlujoCaja/CategoriasMoviento/index.html',
                      {'categorias_movimientos': categorias_movimientos, 'fecha': datetime.now(),
                       'menu_actual': ['flujo_caja', 'categorias_movimientos']})


class CategoriaMovimientoCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Financiero/FlujoCaja/CategoriasMoviento/modal-crear-editar.html',
                      datos_xa_render(self.OPCION))

    def post(self, request):
        categoria_movimiento = CategoriaMovimiento.from_dictionary(request.POST)
        categoria_movimiento.save()
        messages.success(request, 'Se ha creado la categoria de movimiento {0}'.format(categoria_movimiento.nombre))
        return redirect(reverse('financiero:categoria-movimiento-index'))


class CategoriaMovimientoEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        cat_mov = CategoriaMovimiento.objects.get(id=id)
        return render(request, 'Financiero/FlujoCaja/CategoriasMoviento/modal-crear-editar.html',
                      datos_xa_render(self.OPCION, cat_mov))

    def post(self, request, id):
        update_fields = ['nombre', 'descripcion', 'estado']
        cat_mov = CategoriaMovimiento.from_dictionary(request.POST)
        cat_mov.id = id
        cat_mov.estado = request.POST.get('estado', 'False') == 'True'
        cat_mov.save(update_fields=update_fields)
        messages.success(request, 'Se ha editado la categoria de movimiento {0}'.format(cat_mov.nombre))
        return redirect(reverse('Financiero:categoria-movimiento-index'))


class CategoriaMovimientoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            cat_mov = CategoriaMovimiento.objects.get(id=id)
            cat_mov.delete()
            messages.success(request, 'Se ha eliminado la categoria de movimiento {0}'.format(cat_mov.nombre))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error", "mensaje": "Esta categoria de movimiento no puede ser eliminado"
                                                               "porque ya se encuentra en uso."})


# region Métodos de ayuda
def datos_xa_render(opcion: str, cat_mov: CategoriaMovimiento = None) -> dict:
    """
    Datos necesarios para la creación de los html de los Categorias de Movimientos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param cat_mov: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """
    datos = {'opcion': opcion,
             'menu_actual': 'categorias_movimientos'}
    if cat_mov:
        datos['cat_mov'] = cat_mov

    return datos
# endregion