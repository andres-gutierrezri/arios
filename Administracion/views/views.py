# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.db.models import F
from EVA.General.modeljson import ModelDjangoJSON

from Administracion.models import Municipio, CentroPoblado


class CargarMunicipiosSelectJsonView(View):
    def get(self, request, id):
        try:

            municipios = Municipio.objects.filter(departamento_id=id).order_by('nombre')
            mcipios_json = [municipio.to_dict(campos=['id', 'nombre']) for municipio in municipios]
            return JsonResponse(mcipios_json, safe=False)
        except IntegrityError:
            return JsonResponse({"Error": "True"})


class CargarCentroPobladoSelectJsonView(View):
    def get(self, request, id):
        try:
            centropoblados = CentroPoblado.objects.filter(municipio_id=id)
            cpoblados_json = [centropoblado.to_dict(campos=['id', 'nombre']) for centropoblado in centropoblados]
            return JsonResponse(cpoblados_json, safe=False)
        except IntegrityError:
            return JsonResponse({"Error": "True"})
