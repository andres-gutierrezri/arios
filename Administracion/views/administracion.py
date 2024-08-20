# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render

from Administracion.models import Municipio, CentroPoblado, Departamento
from Administracion.models.models import ProductoServicio, SubproductoSubservicio
from EVA.views.index import AbstractEvaLoggedView, AbstractEvaLoggedProveedorView


class PrincipalView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'Administracion/index.html')


class CargarDepartamentosSelectJsonView(AbstractEvaLoggedView):
    def get(self, request, id):
        try:
            departamentos = Departamento.objects.filter(pais_id=id).order_by('nombre')
            departamentos_json = [departamento.to_dict(campos=['id', 'nombre']) for departamento in departamentos]
            return JsonResponse(departamentos_json, safe=False)
        except:
            return JsonResponse({"Error": "True"})


class CargarMunicipiosSelectJsonView(AbstractEvaLoggedView):
    def get(self, request, id):
        try:
            municipios = Municipio.objects.filter(departamento_id=id).order_by('nombre')
            mcipios_json = [municipio.to_dict(campos=['id', 'nombre']) for municipio in municipios]
            return JsonResponse(mcipios_json, safe=False)
        except:
            return JsonResponse({"Error": "True"})


class CargarCentroPobladoSelectJsonView(AbstractEvaLoggedView):
    def get(self, request, id):
        try:
            centropoblados = CentroPoblado.objects.filter(municipio_id=id).order_by('nombre')
            cpoblados_json = [centropoblado.to_dict(campos=['id', 'nombre']) for centropoblado in centropoblados]
            return JsonResponse(cpoblados_json, safe=False)
        except:
            return JsonResponse({"Error": "True"})


PRODUCTO = 1
SERVICIO = 2


class CargarProductoServicio(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        try:
            if id == PRODUCTO:
                respuesta = ProductoServicio.objects.filter(es_servicio=False).order_by('nombre')
            else:
                respuesta = ProductoServicio.objects.filter(es_servicio=True).order_by('nombre')

            respuesta_json = [rsp.to_dict(campos=['id', 'nombre']) for rsp in respuesta]
            return JsonResponse(respuesta_json, safe=False)
        except:
            return JsonResponse({"Error": "True"})


class CargarSubProductosSubServicios(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        try:
            productos_servicios = SubproductoSubservicio.objects.filter(producto_servicio_id=id).order_by('nombre')
            productos_servicios_json = [ps.to_dict(campos=['id', 'nombre']) for ps in productos_servicios]
            return JsonResponse(productos_servicios_json, safe=False)
        except:
            return JsonResponse({"Error": "True"})


