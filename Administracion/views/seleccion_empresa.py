# -*- coding: utf-8 -*-
import json

from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse

from Administracion.models import Empresa
from EVA.views.index import AbstractEvaLoggedView
from Proyectos.models import Contrato
from TalentoHumano.models.colaboradores import ColaboradorContrato, Colaborador


class SeleccionEmpresaModalView(AbstractEvaLoggedView):
    def get(self, request):
        empresas = ColaboradorContrato.objects.filter(colaborador__usuario=request.user).distinct('contrato__empresa')

        return render(request, 'Administracion/_common/_modal_seleccion_empresa.html', {'empresas': empresas})

    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            request.session['empresa'] = Empresa.objects.get(id=int(body['idEmpresa'])).empresa_to_json()
            colaborador = Colaborador(usuario=request.user)
            update_fields = ['contrato_sesion_id']
            colaborador.contrato_sesion_id = 5
            colaborador.save(update_fields=update_fields)
            return JsonResponse({"Mensaje": "OK"})
        except:
            return JsonResponse({"Mensaje": "Falló"})