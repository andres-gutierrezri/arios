from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render

from Administracion.models import Tercero, TipoTercero
from EVA.views.index import AbstractEvaLoggedView


class ProveedorIndexView(AbstractEvaLoggedView):
    def get(self, request):
        proveedores = Tercero.objects.filter(tipo_tercero_id=TipoTercero.PROVEEDOR)
        return render(request, 'Administracion/Tercero/Proveedor/index.html',
                      {'proveedores': proveedores, 'menu_actual': ['proveedores', 'proveedores']})


class ActivarDesartivarProveedorView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            proveedor = Tercero.objects.get(id=id)
            proveedor.estado = False if proveedor.estado else True
            proveedor.save(update_fields=['estado'])

            messages.success(request, 'Se ha eliminado la entidad correctamente')
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "Ha ocurrido un error al realizar la acción Vista"})
