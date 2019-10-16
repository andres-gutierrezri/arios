# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from sqlite3 import IntegrityError

from django.http import JsonResponse
from django.shortcuts import redirect

from django.urls import reverse
from django.views import View

from Administracion.models import Municipio, CentroPoblado


class CargarMunicipiosSelectJsonView(View):
    def get(self, request, id):
        try:
            municipios = Municipio.objects.filter(departamento_id=id).order_by('nombre')
            lista_valores = []
            print(municipios)
            for municipio in municipios:
                lista_valores.append({"id": municipio.id, "nombre": municipio.nombre})

            medidores_json = json.dumps(lista_valores)

            return JsonResponse(medidores_json, safe=False)
        except IntegrityError:
            return JsonResponse({"Error": "True"})


class CargarCentroPobladoSelectJsonView(View):
    def get(self, request, id):
        try:
            centropoblados = CentroPoblado.objects.filter(municipio_id=id)
            lista_valores = []
            for centropoblado in centropoblados:
                lista_valores.append({"id": centropoblado.id, "nombre": centropoblado.nombre})

            medidores_json = json.dumps(lista_valores)

            return JsonResponse(medidores_json, safe=False)
        except IntegrityError:
            return JsonResponse({"Error": "True"})
