# -*- coding: utf-8 -*-
import json

from django.db.models import Q, Subquery
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse

from Administracion.models import Empresa
from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models.colaboradores import Colaborador, ColaboradorEmpresa


class SeleccionEmpresaModalView(AbstractEvaLoggedView):
    def get(self, request):
        empresa_colaborador = ColaboradorEmpresa.objects.filter(colaborador__usuario=request.user).values('empresa_id')
        colaborador = Colaborador.objects.get(usuario=request.user)
        empresas = Empresa.objects.filter(Q(id=colaborador.empresa_id) | Q(id__in=Subquery(empresa_colaborador)))

        empresa_actual = colaborador.empresa_sesion

        return render(request, 'Administracion/_common/_modal_seleccion_empresa.html',
                      {'empresas': empresas,
                       'colaborador': colaborador,
                       'empresa_actual': empresa_actual})

    def post(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            empresa = Empresa.objects.get(id=int(body['idEmpresa']))
            request.session['empresa'] = empresa.to_dict()
            colaborador = Colaborador.objects.get(usuario=request.user)
            colaborador.empresa_sesion_id = int(body['idEmpresa'])
            colaborador.save(update_fields=['empresa_sesion_id'])
            return JsonResponse({"estado": "OK"})
        except:
            return JsonResponse({"estado": "error"})
