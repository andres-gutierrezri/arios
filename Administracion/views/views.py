# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from Administracion.models import Municipio, CentroPoblado
from EVA.General.validacionpermisos import tiene_permisos
from EVA.views.index import AbstractEvaLoggedView


class PrincipalView(AbstractEvaLoggedView):
    def get(self, request):
        if not tiene_permisos(request, 'Administracion', None, None):
            return redirect(reverse('eva-index'))
        else:
            return render(request, 'Administracion/index.html')


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
