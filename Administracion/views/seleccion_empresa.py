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
        empresa_actual = Empresa.objects.get(colaborador__usuario=request.user)
        colaborador = Colaborador.objects.get(usuario=request.user)

        return render(request, 'Administracion/_common/_modal_seleccion_empresa.html', {'empresas': empresas,
                                                                                        'colaborador': colaborador,
                                                                                        'empresa_actual': empresa_actual})

    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            empresa = Empresa.objects.get(id=int(body['idEmpresa']))
            request.session['empresa'] = empresa.empresa_to_json()
            colaborador = Colaborador.objects.get(usuario=request.user)
            colaborador.empresa_sesion_id = int(body['idEmpresa'])
            colaborador.save(update_fields=['empresa_sesion_id'])
            return JsonResponse({"Mensaje": "OK"})
        except:
            return JsonResponse({"Mensaje": "Falló"})